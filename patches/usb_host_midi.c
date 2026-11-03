/* MX-1 USB-processor extension. USB-MIDI 1.0, one cable per direction.
 * No generic audio selection. All DMA buffers remain the stock per-port buffers.
 * RTOS tasks own open/close/queues; USB completion callbacks only publish results.
 */
#include <stdint.h>
#pragma clang section text=".host_text" rodata=".host_rodata"
#define FN(a,t) ((t)(a))
#define U16(p,o) (*(uint16_t *)((uint8_t *)(p)+(o)))
#define U32(p,o) (*(uint32_t *)((uint8_t *)(p)+(o)))
extern int host_config_original(void *, const uint8_t *);
extern int host_tx_open_original(void *);
extern int host_rx_open_original(void *);
extern void host_tx_close_original(void *);
extern void host_rx_close_original(void *);
extern int host_enqueue_original(unsigned, uint32_t);
extern void host_tx_poll_original(void);
extern void host_rx_poll_original(void);
static uint16_t le16(const uint8_t *p) { return p[0] | (uint16_t)p[1]<<8; }
static void zero(uint8_t *p, unsigned n) { while(n--) *p++=0; }

/* Require a bounded standard MS 1.0 alt0, one bulk endpoint per direction,
 * one embedded jack per endpoint. Ignore unrelated audio/control interfaces.
 * Duplicate interface/alt descriptors and a second MS interface are rejected.
 */
int mx1_host_config(uint8_t *r, const uint8_t *cfg) {
    if (U16(r,2)==0x0582) return host_config_original(r,cfg);
    zero(r+8,0x13c-8);
    if (!cfg || cfg[0]!=9 || cfg[1]!=2) return -1;
    unsigned total=le16(cfg+2), niface=cfg[4], seen=0, ms=0, iface=0;
    const uint8_t *start=0,*end=0;
    if(total<9 || total>4096 || !niface || niface>8) return -1;
    for(unsigned o=9;o<total;) {
        const uint8_t *p=cfg+o; unsigned n=p[0];
        if(n<2 || o+n>total) return -1;
        if(p[1]==4) {
            if(n!=9 || p[2]>=niface || p[3]>4) return -1;
            /* All alternate-zero interfaces must be unique and present. */
            if(!p[3]) { if(seen & (1u<<p[2])) return -1; seen|=1u<<p[2]; }
            if(start && !end) end=p;
            if(p[5]==1 && p[6]==3) {
                if(p[3] || p[7] || ++ms!=1 || !p[4] || p[4]>2) return -1;
                start=p; iface=p[2];
            }
        }
        o+=n;
    }
    if(seen != (1u<<niface)-1 || ms!=1) return -1;
    if(!end) end=cfg+total;
    unsigned ids=0, embedded_in=0, embedded_out=0, epseen=0, epcount=0, header=0, cslen=0;
    unsigned incable=0,outcable=0; const uint8_t *ep=0;
    for(const uint8_t *p=start+9;p<end;p+=p[0]) {
        unsigned n=p[0];
        if(p[1]==0x24) {
            if(n<3 || ep) return -1;
            cslen+=n;
            if(p[2]==1) {
                if(n!=7 || header || le16(p+3)!=0x0100) return -1;
                header=le16(p+5);
            } else if(p[2]==2 || p[2]==3) {
                if(n<6 || !p[4] || p[4]>16 || (ids & (1u<<p[4])) || (p[3]!=1 && p[3]!=2)) return -1;
                ids|=1u<<p[4];
                if(p[2]==2) { if(n!=6) return -1; if(p[3]==1) embedded_in|=1u<<p[4]; }
                else { if(n!=9 || p[5]!=1 || !p[6] || p[6]>16 || p[7]!=1) return -1;
                       if(p[3]==1) embedded_out|=1u<<p[4]; }
            } else return -1;
        } else if(p[1]==5) {
            if(ep || (n!=7 && n!=9) || !(p[2]&15) || (p[2]&0x70) || p[3]!=2) return -1;
            unsigned m=le16(p+4), dir=(p[2]&128)?1:2;
            if(!m || m>512 || (m&3) || (epseen&dir) || (n==9 && (p[7]||p[8]))) return -1;
            epseen|=dir; epcount++; ep=p;
        } else if(p[1]==0x25) {
            if(!ep || n!=5 || p[2]!=1 || p[3]!=1 || !p[4] || p[4]>16) return -1;
            if(ep[2]&128) { if(!(embedded_out & (1u<<p[4]))) return -1; incable=1; }
            else { if(!(embedded_in & (1u<<p[4]))) return -1; outcable=1; }
            ep=0;
        } else return -1;
    }
    /* MIDI 1.0 table 6-2 counts header/jacks; appendix B (and FM-1) also
     * counts endpoint descriptors. Accept either exact, validated span. */
    if(ep || !header || (header!=cslen && header!=(unsigned)(end-start-9)) ||
       epcount!=start[4] || (!incable && !outcable)) return -1;
    /* Validate all output-jack source IDs after collecting the complete graph. */
    for(const uint8_t *p=start+9;p<end;p+=p[0])
        if(p[1]==0x24 && p[2]==3 && !(ids&(1u<<p[6]))) return -1;
    r[8]=1; r[9]=cfg[8]*2; r[12]=1; r[15]=iface;
    U16(r,0xd8)=7; r[0xe4]=iface; r[0xe5]=0; r[0xe6]=1;
    r[0xe8]=incable; r[0xe9]=outcable; r[0xea]=incable?2:0; r[0xeb]=outcable?2:0;
    return 0;
}

void mx1_host_select(const uint8_t *info, uint16_t *out) {
    if(le16(info)==0x0582) { FN(0x60007bf9,void(*)(const void*,void*))(info,out); return; }
    if(U32(info,0x64)==1 && (info[0x68] || info[0x69]) &&
       (!info[0x68] || info[0x6a]==2) && (!info[0x69] || info[0x6b]==2)) {
        out[6]=1; out[7]=0;
    }
}

/* Suppress clock, transport, song position and quarter-frame sync on ALL
 * host inputs, including existing Roland devices. No path to AUTO sync. */
void mx1_host_receive(uint32_t word) {
    unsigned cin=word&15, s=(word>>8)&255;
    static const uint8_t lengths[16]={0,0,2,3,3,1,2,3,3,3,3,3,2,2,3,1};
    unsigned n=lengths[cin]; if(!n) return;
    /* Reject embedded realtime statuses too: malformed CIN/SysEx records
       must not bypass the sync-input boundary when the main parser decodes. */
    for(unsigned i=0;i<n;i++) {
        unsigned b=(word>>(8+8*i))&255;
        if(b==0xf8 || b==0xfa || b==0xfb || b==0xfc || b==0xf1 || b==0xf2) return;
    }
    if(s==0xf1 || s==0xf2 || s==0xf8 || s==0xfa || s==0xfb || s==0xfc) return;
    FN(0x01008257,void(*)(uint32_t))(word);
}

typedef struct {
    uint32_t ep[2], flight_ep[2], generation[2], flight_generation[2];
    volatile uint32_t busy[2], ready[2];
    volatile int result[2];
    volatile uint32_t length[2];
    uint32_t queue[32], head, count, urgent[32], urgent_head, urgent_count, flight_length[2], managed[2], fault[2], dropped, errors;
} Port;
__attribute__((section(".host_state"))) static Port ports[4];
static uint8_t *buffer(unsigned port,unsigned tx) { return (uint8_t *)(0x20000000+tx*0x800+port*0x200); }
static void wake(unsigned tx) {
    FN(0x01000877,int(*)(int,int))(*(int16_t *)(0x4000bc08+tx*2),1);
}
/* Completion ABI established by original 6000f60a/6000f7ae: interface,
 * endpoint, {status, transferred_bytes}, user context. Never wait here. */
void mx1_host_done(void *interface, void *ep, const int *result, uintptr_t token) {
    (void)interface; (void)ep;
    unsigned tx=token&1, port=token>>1; if(port>=4) return;
    Port *p=&ports[port];
    p->result[tx]=result[0]; p->length[tx]=(uint32_t)result[1];
    p->ready[tx]=1; p->busy[tx]=0; wake(tx);
}
static int open_port(uint8_t *record,unsigned tx) {
    uint8_t *ep=(uint8_t *)U32(record,4);
    uint8_t *interface=(uint8_t *)U32(ep,0x20);
    uint8_t *dev=(uint8_t *)U32(interface,8);
    unsigned port=record[12];
    if(port>=4) return 0x62;
    Port *p=&ports[port];
    if(U16(dev,0x10)==0x0582) {
        if(p->busy[tx] || p->ready[tx]) return 0x62; /* old DMA still owned */
        p->managed[tx]=0;
        return tx?host_tx_open_original(record):host_rx_open_original(record);
    }
    unsigned m=U16(ep,0x10), speed=U16(dev,0x58);
    if(record[15]!=2 || ep[10]!=2 || ep[9]!=(tx?0:128) ||
       !m || m>512 || (m&3) || (speed!=0x400 && speed!=0) ||
       (speed==0x400 && m!=512) ||
       (speed==0 && m!=8 && m!=16 && m!=32 && m!=64)) return 0x62;
    p->managed[tx]=1; p->generation[tx]++; p->ep[tx]=(uintptr_t)ep; p->fault[tx]=0;
    if(tx) p->head=p->count=p->urgent_head=p->urgent_count=0;
    /* Stock high-speed queue heads stay inactive for generic endpoints. */
    U32(record,0)=0; wake(tx); return 0;
}
int mx1_host_tx_open(uint8_t *r) { return open_port(r,1); }
int mx1_host_rx_open(uint8_t *r) { return open_port(r,0); }
static void close_port(uint8_t *event,unsigned tx) {
    unsigned port=event[4]; if(port>=4) return;
    Port *p=&ports[port];
    if(!p->managed[tx]) { if(tx) host_tx_close_original(event); else host_rx_close_original(event); return; }
    uint32_t ep=p->ep[tx]; p->ep[tx]=0; p->generation[tx]++;
    if(tx) p->head=p->count=p->urgent_head=p->urgent_count=0;
    /* Cancel via stock USB stack. Retain buffer ownership until completion,
     * even if cancellation fails or a replacement attaches immediately. */
    if(ep && p->busy[tx]) FN(0x60009717,int(*)(uint32_t))(ep);
}
void mx1_host_tx_close(uint8_t *e) { close_port(e,1); }
void mx1_host_rx_close(uint8_t *e) { close_port(e,0); }
int mx1_host_enqueue(unsigned port,uint32_t word) {
    if(port>=4) return 1;
    Port *p=&ports[port];
    if(!p->managed[1]) return host_enqueue_original(port,word);
    /* One advertised cable: stock's second cable must not leak into it. */
    if(!p->ep[1] || (p->fault[1]&1) || (word&0xf0)) return 1;
    unsigned status=(word>>8)&255;
    if(status==0xf8 || status==0xfa || status==0xfb || status==0xfc || status==0xf2) {
        if(p->urgent_count==32) { p->dropped++; p->fault[1]=1; p->urgent_count=0; return 1; }
        p->urgent[(p->urgent_head+p->urgent_count)&31]=word; p->urgent_count++; return 1;
    }
    if(p->fault[1]&2) return 1;
    if(p->count==32) { p->dropped++; p->fault[1]|=2; p->count=0; return 1; }
    p->queue[(p->head+p->count)&31]=word; p->count++; return 1;
}
static void poll(unsigned tx) {
    for(unsigned port=0;port<4;port++) {
        Port *p=&ports[port];
        if(p->busy[tx]) continue;
        if(p->ready[tx]) {
            p->ready[tx]=0;
            if(p->flight_generation[tx]==p->generation[tx] && p->ep[tx]) {
                if(p->result[tx] || (p->length[tx]&3) || p->length[tx]>p->flight_length[tx] || (tx && p->length[tx]!=p->flight_length[tx])) {
                    p->errors++; p->fault[tx]=1;
                } else if(!tx) {
                    uint32_t *words=(uint32_t *)buffer(port,0);
                    for(unsigned n=0;n<p->length[0]/4;n++)
                        if(!(words[n]&0xf0)) mx1_host_receive(words[n] | (port<<5));
                }
            }
        }
        if(!p->ep[tx] || (p->fault[tx]&1)) continue;
        unsigned n;
        if(tx) {
            n=0; uint32_t *dst=(uint32_t *)buffer(port,1);
            while(n<16 && p->urgent_count) {
                dst[n++]=p->urgent[p->urgent_head]; p->urgent_head=(p->urgent_head+1)&31; p->urgent_count--;
            }
            while(n<16 && p->count) {
                dst[n++]=p->queue[p->head]; p->head=(p->head+1)&31; p->count--;
            }
            if(!n) continue;
            n*=4;
        } else n=U16(p->ep[0],0x10);
        p->flight_ep[tx]=p->ep[tx]; p->flight_generation[tx]=p->generation[tx];
        p->flight_length[tx]=n; p->busy[tx]=1;
        int rc=FN(0x60009465,int(*)(uint32_t,void*,unsigned,void*,uintptr_t,int,unsigned))
            (p->ep[tx],buffer(port,tx),n,mx1_host_done,(port<<1)|tx,tx?100:-1,0);
        if(rc) { p->busy[tx]=0; p->fault[tx]=1; p->errors++; }
    }
}
void mx1_host_tx_poll(void) { host_tx_poll_original(); poll(1); }
void mx1_host_rx_poll(void) { host_rx_poll_original(); poll(0); }
