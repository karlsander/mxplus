/* Experimental FM-1 input, app_usb only. See research/fm1-host-audio.md.
 * Manager: interfaces/readiness. OHCI worker: ED/ITD ownership. Audio task:
 * consumer and stock DSP calls. No USB calls or allocation in an interrupt.
 */
#include <stdint.h>
#include <stddef.h>
#pragma clang section text=".host_audio" rodata=".host_audio_rodata"
#define FN(a,t) ((t)(a))
#define U16(p,o) (*(uint16_t *)((uint8_t *)(p)+(o)))
#define U32(p,o) (*(uint32_t *)((uint8_t *)(p)+(o)))
#define V32(p,o) (*(volatile uint32_t *)((uint8_t *)(p)+(o)))
#define PTR(p,o) ((uint8_t *)(uintptr_t)U32(p,o))
#define NTD 17
#define NPACKET 8
static void barrier(void) { __asm__ volatile("dmb" ::: "memory"); }
static void zero(void *v,unsigned n) { uint8_t *p=v; while(n--) *p++=0; }
static unsigned le16(const uint8_t *p) { return p[0]|(unsigned)p[1]<<8; }
static const uint8_t fm1_rate[3]={0x44,0xac,0};

/* Deliberately accept only the measured FM-1 streaming profile. The parser
 * checks descriptor boundaries first, then one PCM16 stereo alt and endpoint.
 * Other devices continue through the MIDI-only or stock Roland paths. */
int mx1_audio_profile(const uint8_t *c) {
    if(!c || c[0]!=9 || c[1]!=2 || c[4]!=3) return 0;
    unsigned total=le16(c+2), active=0, seen=0, format=0, general=0, endpoint=0, cs=0;
    if(total<9 || total>4096) return 0;
    for(unsigned o=9;o<total;) {
        const uint8_t *d=c+o; unsigned n=d[0];
        if(n<2 || o+n>total) return 0;
        if(d[1]==4) {
            if(n!=9) return 0;
            active=d[2]==1 && d[3]==1;
            if(active && (++seen!=1 || d[4]!=1 || d[5]!=1 || d[6]!=2 || d[7])) return 0;
        } else if(active) {
            if(d[1]==0x24 && n>=3 && d[2]==1) {
                if(n!=7 || ++general!=1 || d[3]!=2 || le16(d+5)!=1) return 0;
            } else if(d[1]==0x24 && n>=3 && d[2]==2) {
                if(n!=11 || ++format!=1 || d[3]!=1 || d[4]!=2 || d[5]!=2 ||
                   d[6]!=16 || d[7]!=1 || d[8]!=0x44 || d[9]!=0xac || d[10]) return 0;
            } else if(d[1]==5) {
                if(n!=9 || ++endpoint!=1 || d[2]!=0x84 || d[3]!=5 ||
                   le16(d+4)!=184 || d[6]!=1 || d[7] || d[8]) return 0;
            } else if(d[1]==0x25) {
                if(n!=7 || ++cs!=1 || d[2]!=1 || d[3]!=1 || d[4] || d[5] || d[6]) return 0;
            } else return 0;
        }
        o+=n;
    }
    return seen==1 && general==1 && format==1 && endpoint==1 && cs==1;
}

typedef struct __attribute__((aligned(32))) {
    volatile uint32_t control, page, next, end;
    volatile uint16_t psw[8];
    int16_t pcm[96]; /* 184 bytes advertised; padding keeps the next ITD aligned. */
} IsoTD;
typedef struct { uint32_t frames; int16_t pcm[92]; } Packet;
typedef struct __attribute__((aligned(32))) {
    /* First 16 bytes are an OHCI ED. Remaining fields match stock ED list ABI. */
    volatile uint32_t control, tail, head, next;
    uint32_t flags, self, following, previous, owner;
    uint32_t spare[7];
} IsoED;
typedef struct {
    uint8_t *dev, *ep, *interface, *controller;
    volatile uint32_t wanted, claimed, phase, cancel_queued;
    uint32_t generation, next_frame, close_frame, cost, tail_slot;
    volatile uint32_t write_count, read_count;
    uint32_t quarter, primed, retry_tick;
    uint32_t packets, malformed, overflow, underrun, missed, dsp_errors;
    IsoED ed;
    IsoTD td[NTD];
    Packet packets_in[NPACKET];
    int32_t samples[24], discard[24];
} AudioPort;
__attribute__((section(".host_audio_state"))) AudioPort mx1_audio_ports[4];
/* Keep diagnostics AFTER the established DMA/sample layout. Only the OHCI
 * worker reads controller state; the MIDI TX task reads these RAM snapshots. */
typedef struct {
    uint8_t *dev;
    volatile uint32_t stage, result, controller, control, flags, cc, frame;
    uint32_t sent, pending, sysex;
} AudioDiagnostic;
__attribute__((section(".host_audio_diagnostics"))) static AudioDiagnostic diagnostics[4];
/* Appended after established audio/DMA and A1 diagnostic layouts. */
typedef struct {
    uint8_t *dev;
    uint8_t input[16], reply[240];
    unsigned input_n, reply_pos;
    volatile unsigned reply_n, busy, mode, mode_until;
    unsigned sequence, errors, dropped, tone_phase, tone_tick;
    volatile unsigned snapshot_seq;
    uint32_t raw[102];
    uint32_t topology[12];
    volatile unsigned probe, probe_done, probe_result;
    unsigned heartbeat;
} DebugPort;
__attribute__((section(".host_debug_state"))) static DebugPort debug_ports[4];
__attribute__((section(".host_debug_state"))) static volatile uint32_t debug_ticks;
/* The original TX task waits on this flag at 0100921c. Only signal it;
 * all packet construction and USB submission stay in that task. */
static void debug_wake_tx(void) {
    int flag=*(int16_t *)0x4000bc0a;
    if(flag>0) FN(0x01000877,int(*)(int,int))(flag,1);
}
static void debug_capture(AudioPort *p);
static void debug_done(void *,void *,unsigned,int,uintptr_t);
static void debug_probe(uint8_t *event);
static void ehci_tick(void);
static AudioDiagnostic *diagnostic(AudioPort *p) { return &diagnostics[p-mx1_audio_ports]; }
static void stage(AudioPort *p,unsigned value,int result) {
    AudioDiagnostic *d=diagnostic(p);
    d->result=result<0?(unsigned)-result:(unsigned)result;
    barrier(); d->stage=value;
}
_Static_assert(sizeof(IsoTD)==224,"ITD stride/alignment");
_Static_assert(sizeof(IsoED)==64,"ED software layout");
static uint8_t *record(void *dev) { return FN(0x60008d4b,uint8_t *(*)(void*))(dev); }
static unsigned frame(AudioPort *p) { return U32(PTR(p->controller,8),0x3c)&65535; }
static void post(AudioPort *p,unsigned event) {
    uint32_t message[3]={event,(uintptr_t)p->dev,0};
    FN(0x60007e11,int(*)(void*))(message);
}
static void cancel(AudioPort *p) {
    /* Publish intent only. The next ISO completion retires the ED in the
     * OHCI worker (including device-not-responding completions on unplug).
     * Never enqueue a retry using a device/endpoint the manager may free. */
    p->wanted=0; barrier();
}
static AudioPort *for_device(void *dev) {
    for(unsigned i=0;i<4;i++) if(mx1_audio_ports[i].claimed && mx1_audio_ports[i].dev==dev) return &mx1_audio_ports[i];
    return 0;
}
static void start_done(void *dev,void *ep,unsigned bytes,int status,uintptr_t token) {
    (void)dev; (void)ep; (void)bytes;
    AudioPort *p=(AudioPort *)token;
    if(status) {
        if(diagnostic(p)->stage<0x40) stage(p,0x46,status);
        p->wanted=0; p->claimed=0; return;
    }
    if(p->wanted && p->phase==2) post(p,5);
}
static void try_open(uint8_t *dev,uint8_t *r) {
    unsigned port=U16(r,2); if(port>=4 || !(r[0]&1) || U32(r,4)) return;
    AudioPort *p=&mx1_audio_ports[port];
    if(p->claimed || U16(dev,0x10)!=0x1209 || U16(dev,0x12)!=1 || U16(dev,0x58)) return;
    const uint8_t *c=FN(0x60009d2d,const uint8_t *(*)(void*,unsigned))(dev,0);
    if(!mx1_audio_profile(c)) return;
    /* Controller 1 is EHCI, including full-speed devices behind a hub.
     * The custom request hook is installed ONLY on OHCI. Never submit its
     * private start callback to the unmodified EHCI request handler. */
    if(U16(dev,0x4a)!=0 && !(U16(dev,0x4a)==1 && debug_ports[port].probe==5)) {
        stage(p,0x48,-5); return;
    }
    for(unsigned i=0;i<U16(r,0x20) && i<8;i++) {
        uint8_t *n=PTR(r,0x28+i*8);
        if(!n || n[0x13]!=1 || n[0x14]!=1 || n[0x15]!=1) continue;
        stage(p,4,0);
        uint8_t *ep=0;
        int lookup=FN(0x600096c7,int(*)(void*,int,int,int,int,int,void*))(n,0,128,1,0,0,&ep);
        if(lookup) { stage(p,0x44,lookup); return; }
        if(!ep || ep[8]!=0x84 || ep[9]!=128 || ep[10]!=1 || U16(ep,0x10)!=184 || U16(ep,0xe)!=1) {
            stage(p,0x45,0); return;
        }
        p->dev=dev; p->ep=ep; p->interface=n; p->generation++;
        p->cancel_queued=0; p->wanted=1; p->claimed=1; barrier();
        /* Stock DSP initialization stays in manager task, before publication
         * to the audio task. Its serial interface is the original open path. */
        FN(0x600079ef,void(*)(unsigned,unsigned,unsigned))(port,1,44100);
        stage(p,5,0);
        int e=FN(0x6000c277,int(*)(void*,void*,unsigned,unsigned,unsigned,void*,unsigned,void*,uintptr_t,unsigned))
            (dev,ep,0,0,0,0,0,(void*)start_done,(uintptr_t)p,0);
        if(e) { stage(p,0x45,e); p->wanted=0; p->claimed=0; }
        return;
    }
}
void mx1_audio_setup(uint8_t *event) {
    uint8_t *dev=PTR(event,4), *r=record(dev);
    if(!r || !(r[0]&1) || U32(r,4) || U16(dev,0x10)!=0x1209 || U16(dev,0x12)!=1 || U16(dev,0x58)) return;
    if(for_device(dev)) return;
    const uint8_t *c=FN(0x60009d2d,const uint8_t *(*)(void*,unsigned))(dev,0);
    if(!mx1_audio_profile(c)) return;
    unsigned port=U16(r,2); if(port>=4) return;
    AudioPort *p=&mx1_audio_ports[port]; AudioDiagnostic *d=diagnostic(p);
    zero(&debug_ports[port],sizeof debug_ports[port]); debug_ports[port].dev=dev;
    zero(d,sizeof *d); d->dev=dev; d->controller=U16(dev,0x4a); stage(p,1,0);
    DebugPort *db=&debug_ports[port];
    /* Cached object fields, not controller MMIO. +ec is the parent hub
     * object, whose +4 is the upstream USB device and +8..+20 its ports.
     * Record raw identifiers; no inferred board/chip identity. */
    uint8_t *hub=PTR(dev,0xec),*parent=hub?PTR(hub,4):0;
    db->topology[0]=U16(dev,0x4a); db->topology[1]=U16(dev,0x4c);
    db->topology[2]=U16(dev,0x58); db->topology[3]=U16(dev,0x48);
    db->topology[4]=(uintptr_t)hub; db->topology[5]=(uintptr_t)parent;
    if(parent) {
        db->topology[6]=U16(parent,0x4a); db->topology[7]=U16(parent,0x4c);
        db->topology[8]=U16(parent,0x58); db->topology[9]=U16(parent,0x10);
        db->topology[10]=U16(parent,0x12);
    }
    if(hub) for(unsigned i=1;i<=7;i++) if(PTR(hub,4+i*4)==dev) db->topology[11]=i;
    /* Keep a working MIDI/debug baseline on the observed controller. The
     * bounded probe command can exercise each control/lookup separately. */
    if(U16(dev,0x4a)!=0) { stage(p,0x48,-5); return; }
    /* UAC1 endpoint sampling-frequency SET_CUR, followed by AS alt1.
     * Three little-endian bytes, fixed advertised rate. */
    int e=FN(0x60009559,int(*)(void*,unsigned,unsigned,unsigned,unsigned,unsigned,void*,unsigned))
       (dev,0x22,1,0x100,0x84,3,(void*)fm1_rate,0);
    if(e) { stage(p,0x41,e); return; }
    stage(p,2,0);
    e=FN(0x60009559,int(*)(void*,unsigned,unsigned,unsigned,unsigned,unsigned,void*,unsigned))
       (dev,1,11,1,1,0,0,0);
    if(e) { stage(p,0x42,e); return; }
    stage(p,3,0);
    try_open(dev,r);
}
void mx1_audio_bind(uint8_t *event) {
    FN(0x60008427,void(*)(void*))(event);
    uint8_t *n=PTR(event,4), *dev=PTR(n,8), *r=record(dev);
    if(r) try_open(dev,r);
}
void mx1_audio_remove(uint8_t *event) {
    uint8_t *n=PTR(event,4); AudioPort *p=for_device(PTR(n,8));
    if(p && p->interface==n) cancel(p);
    FN(0x6000852b,void(*)(void*))(event);
}
void mx1_audio_ready(uint8_t *event) {
    if(U32(event,8)==0x3242444d) { debug_probe(event); return; }
    AudioPort *p=for_device(PTR(event,4));
    if(!p) { FN(0x600088d3,void(*)(void*))(event); return; }
    uint8_t *r=record(p->dev);
    if(r && p->wanted && p->phase==2 && !(r[0]&2)) {
        r[12]=1; r[13]=0; r[15]=0; r[16]=0;
        U16(r,0x12)=1; U32(r,0x14)=44100;
        r[0x18]=2; r[0x19]=1; r[0x1a]=2; r[0x1b]=0;
        FN(0x60008d61,void(*)(void*,unsigned))(r,2);
    }
}
extern void host_audio_close_original(void *);
void mx1_audio_close(uint8_t *r) {
    AudioPort *p=for_device(PTR(r,8));
    /* OHCI may already have retired the endpoint by the time the manager
     * handles final device removal. It still belongs to this audio path. */
    if(!p && U16(r,2)<4 && U16(r,0x66)==0x1209 && U16(r,0x68)==1 &&
       mx1_audio_ports[U16(r,2)].dev==PTR(r,8)) p=&mx1_audio_ports[U16(r,2)];
    if(!p) { host_audio_close_original(r); return; }
    cancel(p);
    FN(0x60007a1b,void(*)(unsigned,unsigned))(U16(r,2),1);
}

/* OHCI worker only below. No stock general-TD structure is used for ISO. */
static void snapshot(AudioPort *p) {
    AudioDiagnostic *d=diagnostic(p);
    if(p->phase!=2 || d->controller!=0) return;
    uint8_t *regs=PTR(p->controller,8);
    unsigned control=V32(regs,4), head=p->ed.head;
    d->control=(control&0x3f)|((control&0xc0)==0x80?0x40:0);
    d->flags=!!p->claimed | (!!p->wanted<<1) | (!!(p->ed.control&0x4000)<<2) |
        (((head&~15u)==p->ed.tail)<<3) | ((head&1)<<4);
    uintptr_t t=head&~31u, base=(uintptr_t)p->td;
    d->cc=t>=base && t<base+sizeof p->td && (t-base)%sizeof(IsoTD)==0?U32((void*)t,0)>>28:127;
    d->frame=frame(p);
    debug_capture(p);
}
static void prepare(AudioPort *p,unsigned i,unsigned next) {
    IsoTD *t=&p->td[i]; uintptr_t data=(uintptr_t)t->pcm;
    t->page=data&~4095u; t->end=data+183; t->next=(uintptr_t)&p->td[next];
    for(unsigned j=0;j<8;j++) t->psw[j]=0xe000;
    t->psw[0]=0xe000|(data&4095);
    t->control=0xe0000000|(p->next_frame++&65535); /* one frame, interrupt immediately */
}
static unsigned bandwidth(AudioPort *p) {
    unsigned unused;
    unsigned sum=FN(0x600125dd,unsigned(*)(void*,unsigned,void*))(p->controller,31,&unused);
    U32(p->controller,0x53c)=sum; return sum;
}
static void unlink_ed(AudioPort *p) {
    IsoED *e=&p->ed; e->control|=0x4000; barrier();
    uint32_t root=(uintptr_t)p->controller+0x28;
    if(e->previous==root) U32(PTR(p->controller,0x34),0)=e->next;
    else U32(PTR((void*)e->previous,8),12)=e->next;
    U32((void*)e->previous,0)=e->following;
    U32((void*)e->following,4)=e->previous;
    barrier(); U16(p->controller,0x38)-=p->cost; bandwidth(p);
}
static int begin(AudioPort *p) {
    if(!p->wanted || p->phase) { stage(p,0x47,-9); return -9; }
    uint8_t *dev=p->dev, *ep=p->ep;
    if(U16(dev,0x58) || U16(dev,0x4a)!=0) { stage(p,0x48,-5); return -5; }
    p->controller=PTR(PTR((void*)0x6002b0e8,0),0x40);
    uint8_t *regs=PTR(p->controller,8);
    unsigned control=V32(regs,4);
    diagnostic(p)->control=(control&0x3f)|((control&0xc0)==0x80?0x40:0);
    if((control&0xc0)!=0x80) { stage(p,0x49,-5); return -5; }
    uint8_t wrapper[40]; zero(wrapper,sizeof wrapper);
    if(FN(0x60013087,int(*)(void*,void*,void*,void*))(p->controller,dev,ep,wrapper)) {
        stage(p,0x4a,-5); return -5;
    }
    p->cost=U32(wrapper,0x1c);
    U16(p->controller,0x38)+=p->cost;
    if(bandwidth(p)>((U32(regs,0x34)>>16)&0x7fff)) {
        U16(p->controller,0x38)-=p->cost; bandwidth(p); stage(p,0x4b,-5); return -5;
    }
    zero(&p->ed,sizeof p->ed); zero(p->td,sizeof p->td);
    p->write_count=p->read_count=p->quarter=p->primed=0;
    p->next_frame=(frame(p)+3)&65535;
    for(unsigned i=0;i<NTD-1;i++) prepare(p,i,i+1);
    p->tail_slot=NTD-1;
    IsoED *e=&p->ed;
    e->control=U32(wrapper,8)|0x4000; e->tail=(uintptr_t)&p->td[NTD-1]; e->head=(uintptr_t)&p->td[0];
    e->self=e->owner=(uintptr_t)e;
    uint32_t root=(uintptr_t)p->controller+0x28;
    uint32_t previous=U32((void*)root,4);
    e->following=root; e->previous=previous;
    if(previous==root) {
        uint8_t *link=PTR(p->controller,0x34); e->next=U32(link,0); U32(link,0)=(uintptr_t)e;
    } else { e->next=0; U32(PTR((void*)previous,8),12)=(uintptr_t)e; }
    U32((void*)previous,0)=(uintptr_t)&e->following; U32((void*)root,4)=(uintptr_t)&e->following;
    barrier(); e->control&=~0x4000u; V32(regs,4)|=0xc;
    barrier(); p->phase=2; return 0;
}
int mx1_ohci_request(void *dev,void *ep,unsigned flags,unsigned a,unsigned b,void *buf,unsigned len,void *callback,uintptr_t token) {
    AudioPort *p=for_device(dev);
    if(callback==(void*)debug_done) {
        if(!p || ep!=p->ep || p->phase!=2 || (token&3)!=(unsigned)(p-mx1_audio_ports) ||
           (token>>2)!=(p->generation&0x3fffffff)) return -9;
        snapshot(p); debug_done(dev,ep,0,0,token); return 0;
    }
    if(p && ep==p->ep && callback==(void*)start_done && token==(uintptr_t)p) {
        stage(p,6,0);
        int result=begin(p);
        if(!result) { stage(p,7,0); snapshot(p); start_done(dev,ep,0,0,token); }
        return result;
    }
    return FN(0x600132d7,int(*)(void*,void*,unsigned,unsigned,unsigned,void*,unsigned,void*,uintptr_t))
        (dev,ep,flags,a,b,buf,len,callback,token);
}
static void stop_worker(AudioPort *p) {
    p->wanted=0;
    if(p->phase==2) { unlink_ed(p); p->close_frame=frame(p); p->phase=3; }
    if(p->phase==3) V32(PTR(p->controller,8),0x10)=4; /* SOF until retirement */
}
int mx1_ohci_cancel(void *dev,void *ep) {
    AudioPort *p=for_device(dev);
    if(!p || ep!=p->ep || diagnostic(p)->controller) return FN(0x600136ad,int(*)(void*,void*))(dev,ep);
    stop_worker(p);
    return 0;
}
extern void host_ohci_bind_original(unsigned,void*);
extern int host_ohci_done_original(uintptr_t);
static IsoTD *owned(uintptr_t t,AudioPort **out) {
    for(unsigned i=0;i<4;i++) {
        AudioPort *p=&mx1_audio_ports[i]; uintptr_t base=(uintptr_t)p->td;
        if(!diagnostic(p)->controller && t>=base && t<base+sizeof p->td && (t-base)%sizeof(IsoTD)==0) { *out=p; return (IsoTD *)t; }
    }
    return 0;
}
static void completed(AudioPort *p,IsoTD *t) {
    if(p->phase!=2) return;
    if(!p->wanted) { stop_worker(p); return; }
    unsigned status=t->psw[0], bytes=status&2047, cc=status>>12;
    if((cc==0 || cc==9) && bytes>=160 && bytes<=184 && !(bytes&3) && !(t->control>>28)) {
        unsigned w=p->write_count;
        if(w-p->read_count<NPACKET) {
            Packet *q=&p->packets_in[w&(NPACKET-1)];
            for(unsigned i=0;i<bytes/2;i++) q->pcm[i]=t->pcm[i];
            q->frames=bytes/4; barrier(); p->write_count=w+1; p->packets++;
        } else p->overflow++;
    } else p->malformed++;
    unsigned now=frame(p);
    if((int16_t)(p->next_frame-now)<2) { p->next_frame=(now+3)&65535; p->missed++; }
    unsigned i=(unsigned)(t-p->td), old=p->tail_slot;
    prepare(p,old,i); barrier();
    p->ed.tail=(uintptr_t)t; p->tail_slot=i;
}
int mx1_ohci_done(uintptr_t head) {
    uintptr_t normal=0, *normal_tail=&normal, iso=0;
    /* Preserve the original newest-first general list, reverse custom ISO
     * completions into chronological order before feeding and rearming. */
    for(uintptr_t t=head&~15u;t;) {
        uintptr_t next=U32((void*)t,8); AudioPort *p=0;
        if(owned(t,&p)) { U32((void*)t,8)=iso; iso=t; }
        else { *normal_tail=t; normal_tail=(uintptr_t *)(t+8); }
        t=next;
    }
    *normal_tail=0;
    while(iso) { IsoTD *t=(IsoTD *)iso; iso=t->next; AudioPort *p=0; owned((uintptr_t)t,&p); completed(p,t); }
    return normal?host_ohci_done_original(normal):0;
}
int mx1_ohci_event(unsigned controller,unsigned event) {
    for(unsigned i=0;i<4;i++) snapshot(&mx1_audio_ports[i]);
    int result=FN(0x60013963,int(*)(unsigned,unsigned))(controller,event);
    for(unsigned i=0;i<4;i++) {
        AudioPort *p=&mx1_audio_ports[i]; if(p->phase!=3 || diagnostic(p)->controller) continue;
        uint8_t *regs=PTR(p->controller,8);
        if((uint16_t)(frame(p)-p->close_frame)>=2 && !U32(PTR(p->controller,12),0x84) &&
           !V32(regs,0x30) && (V32(regs,0x1c)&~15u)!=(uintptr_t)&p->ed) {
            p->phase=0; barrier(); p->claimed=0;
        } else V32(regs,0x10)=4;
    }
    return result;
}

/* Experimental, non-commercial SysEx for the already installed FM-1 monitor.
 * A report accompanies a changed start state and each transmitted note-on.
 * All five packets fit in one MIDI transfer; never insert into user SysEx.
 * No musical messages are generated and no queue capacity is consumed. */
unsigned mx1_audio_monitor(unsigned port,void *ep,uint32_t *words,unsigned n) {
    if(port>=4 || n>16 || !ep) return n;
    AudioPort *p=&mx1_audio_ports[port]; AudioDiagnostic *d=diagnostic(p);
    if(!d->stage || PTR(PTR(ep,0x20),8)!=d->dev) return n;
    for(unsigned i=0;i<n;i++) {
        unsigned w=words[i], cin=w&15, s=(w>>8)&255;
        if(cin==4) d->sysex=1;
        else if(cin==6 || cin==7 || (cin==5 && s==0xf7) || (s>=0x80 && s<0xf0)) d->sysex=0;
        if(cin==9 && (s&0xf0)==0x90 && (w>>24)) d->pending=1;
    }
    unsigned signature=(d->stage&127)|((d->result&127)<<8)|(p->phase<<16);
    if(n>11 || d->sysex || (!d->pending && d->sent==signature)) return n;
    uint8_t bytes[15]={0xf0,0x7d,0x4d,d->stage&127,d->controller&127,d->result&127,
        p->phase&127,d->control&127,d->flags&127,d->cc&127,
        p->packets<127?p->packets:127,p->malformed<127?p->malformed:127,
        d->frame&127,(d->frame>>7)&127,0xf7};
    for(unsigned i=0;i<5;i++) words[n++]=(i==4?7:4)|((uint32_t)bytes[i*3]<<8)|
        ((uint32_t)bytes[i*3+1]<<16)|((uint32_t)bytes[i*3+2]<<24);
    d->sent=signature; d->pending=0; return n;
}
int mx1_ohci_reset(unsigned controller,unsigned operation) {
    /* Remove static EDs before the stock controller teardown frees its lists. */
    for(unsigned i=0;i<4;i++) {
        AudioPort *p=&mx1_audio_ports[i];
        if(diagnostic(p)->controller) continue;
        if(p->phase==2) { p->wanted=0; unlink_ed(p); p->close_frame=frame(p); p->phase=3; }
    }
    int result=FN(0x600127b7,int(*)(unsigned,unsigned))(controller,operation);
    if(!result && operation==2) {
        /* Successful stock destroy has reset/stopped OHCI and released HCCA.
         * Never dereference that freed controller state on a later event. */
        for(unsigned i=0;i<4;i++) {
            AudioPort *p=&mx1_audio_ports[i];
            if(p->phase==3 && !diagnostic(p)->controller) { p->phase=0; p->controller=0; barrier(); p->claimed=0; }
        }
    }
    return result;
}
void mx1_ohci_bind(unsigned controller,uint8_t *driver) {
    host_ohci_bind_original(controller,driver);
    U32(driver,8)=(uintptr_t)mx1_ohci_reset;
    U32(driver,12)=(uintptr_t)mx1_ohci_request;
    U32(driver,16)=(uintptr_t)mx1_ohci_cancel;
    U32(driver,0x2c)=(uintptr_t)mx1_ohci_event;
}

/* The original audio task serializes all DSP submissions, including Roland.
 * There are four invocations per full-speed frame. Keep packet frame counts
 * intact across those calls, allowing the stock converter to measure drift. */
extern void host_audio_tick_original(unsigned);
void mx1_audio_tick(unsigned microframe) {
    host_audio_tick_original(microframe);
    debug_ticks++;
    ehci_tick();
    if(!(debug_ticks&4095)) {
        for(unsigned port=0;port<4;port++) if(debug_ports[port].dev) {
            debug_wake_tx(); break;
        }
    }
    for(unsigned port=0;port<4;port++) {
        AudioPort *p=&mx1_audio_ports[port];
        if(!p->claimed) continue;
        if(!p->wanted) continue;
        if(p->phase!=2) continue;
        DebugPort *d=&debug_ports[port];
        if(d->mode && (int32_t)(debug_ticks-d->mode_until)>=0) d->mode=0;
        unsigned r=p->read_count, available=p->write_count-r;
        if(!p->primed && available>=2) { p->primed=1; p->quarter=0; }
        unsigned frames=11;
        if(p->primed && available) {
            Packet *q=&p->packets_in[r&(NPACKET-1)]; barrier();
            unsigned first=q->frames*p->quarter/4, end=q->frames*(p->quarter+1)/4;
            frames=end-first;
            for(unsigned j=0;j<frames*2;j++) p->samples[j]=(int32_t)q->pcm[first*2+j]*65536;
            if(++p->quarter==4) { p->quarter=0; barrier(); p->read_count=r+1; }
        } else {
            if(p->primed) { p->underrun++; p->primed=0; }
            zero(p->samples,sizeof p->samples);
        }
        if(d->mode==1) zero(p->samples,sizeof p->samples);
        else if(d->mode==2) {
            /* Opt-in -24 dBFS triangle, bypassing USB sample arrival, through
             * the same converter. 441 frames per 40 quarter-ms calls. */
            frames=11+(++d->tone_tick%40==0);
            for(unsigned j=0;j<frames;j++) {
                d->tone_phase=(d->tone_phase+220)%44100;
                int x=(int)(d->tone_phase<22050?d->tone_phase:44100-d->tone_phase);
                int32_t sample=(x*4096/22050-2048)*65536;
                p->samples[j*2]=p->samples[j*2+1]=sample;
            }
        }
        uint32_t block[12]={1,0x00020001,0,(uintptr_t)p->samples,0,frames*8,0,2,(uintptr_t)p->discard,0,0,0};
        if(FN(0x010088dd,int(*)(unsigned,void*))(port,block)) {
            p->dsp_errors++; cancel(p); post(p,6);
        }
    }
}

#include "usb_host_ehci.inc"
#include "usb_host_debug.inc"
