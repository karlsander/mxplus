/* B5: one explicitly started FM-1 split-ISO IN stream. See research/fm1-ehci.md.
 * HCD worker owns list edits and DMA retirement. The audio task only queues a
 * controller-status callback (no device pointer) as a lost-IOC fallback.
 * The live periodic table is Roland's 4000b000, NOT controller context +8.
 * Do not enable/disable schedules, reset hardware, or change stock iTD/QHs.
 */
#define ENSLOT 16
typedef struct {
    AudioPort *owner;
    uint8_t *regs, *table;
    uint32_t slot_frame[ENSLOT], old_link[ENSLOT], last_status[ENSLOT];
    uint32_t linked, endpoint, mask, deadline, serviced, events, reason, bad_link;
    uint32_t peak[2], nonzero, last_bytes, status, max_walk;
    volatile uint32_t poll_pending;
} EhciAudio;
__attribute__((section(".host_ehci_state"))) static EhciAudio ehci;
static unsigned ehci_frame(void) { return (V32(ehci.regs,12)>>3)&2047; }
static int ehci_current(AudioPort *p) {
    uint8_t *driver=PTR((void*)0x6002b0e8,4);
    return driver && p->controller && PTR(driver,0x40)==p->controller;
}
static void ehci_snapshot(AudioPort *p) {
    DebugPort *d=&debug_ports[p-mx1_audio_ports]; AudioDiagnostic *a=diagnostic(p);
    if(!ehci_current(p)) return;
    uint8_t *r=ehci.regs;
    a->control=V32(r,0); a->flags=ehci.linked; a->cc=ehci.status&255; a->frame=ehci_frame();
    d->snapshot_seq++; barrier(); zero(d->raw,sizeof d->raw);
    uint32_t words[]={(uintptr_t)p->controller,(uintptr_t)r,(uintptr_t)ehci.table,
        V32(PTR(p->controller,0),8),V32(r,0),V32(r,4),V32(r,8),V32(r,12),
        V32(r,16),V32(r,20),V32(r,24),V32(r,64),p->phase,(unsigned)(p-mx1_audio_ports),
        ehci.linked,ehci.deadline,ehci.serviced,ehci.poll_pending,ehci.events,ehci.reason,
        ehci.bad_link,ehci.max_walk,p->next_frame,p->tail_slot,p->packets,p->malformed,p->missed,
        ehci.peak[0],ehci.peak[1],ehci.nonzero,ehci.last_bytes,ehci.status,ehci.endpoint,
        ehci.mask,p->generation,U16((void*)0x4000bbb0,0)};
    for(unsigned i=0;i<36;i++) d->raw[i]=words[i];
    for(unsigned i=0;i<ENSLOT;i++) {
        d->raw[36+i*2]=ehci.slot_frame[i]; d->raw[37+i*2]=V32(&p->td[i],12);
        d->raw[70+i*2]=ehci.old_link[i]; d->raw[71+i*2]=ehci.last_status[i];
    }
    barrier(); d->snapshot_seq++;
}
/* Admission is intentionally narrower than a bandwidth allocator. Accept only
 * the eight inactive stock audio iTDs, original dummy roots, and up to four
 * small high-speed interrupt QHs on each path. No other FS periodic endpoint,
 * active stock audio, foreign iTD, siTD or FSTN may share this experiment.
 * Bulk/control continue in the independent asynchronous schedule.
 */
static int ehci_path(AudioPort *p,uint32_t link) {
    unsigned count=0, interrupts=0;
    while(!(link&1)) {
        uintptr_t ptr=link&~31u; unsigned type=link&6,dummy=0;
        if(++count>24) break;
        int stock=ptr>=0x4000b420 && ptr<0x4000b620 && !((ptr-0x4000b420)&63);
        if(!stock) for(unsigned i=0;i<10;i++) if(ptr==U32(p->controller,0x30+i*4)) dummy=1;
        if(type==0 && (stock || dummy)) {
            for(unsigned j=0;j<8;j++) if(V32((void*)ptr,4+j*4)&0x80000000u) goto bad;
        } else if(type==2 && dummy) {
            /* Dummy QHs have no active transaction overlay. */
            if(V32((void*)ptr,24)&128) goto bad;
        } else if(type==2 && ptr>=0x604807f8 && ptr<=0x60481c90) {
            unsigned caps=V32((void*)ptr,4), split=V32((void*)ptr,8);
            if(((caps>>12)&3)!=2 || !((caps>>16)&2047) || ((caps>>16)&2047)>8 ||
               ((split>>30)&3)!=1 || ++interrupts>4) goto bad;
        } else goto bad;
        link=V32((void*)ptr,0);
    }
    if(link&1) { if(count>ehci.max_walk) ehci.max_walk=count; return 1; }
bad:
    ehci.bad_link=link; return 0;
}
static int ehci_unlink(AudioPort *p,unsigned i) {
    if(!(ehci.linked&(1u<<i))) return 1;
    uint8_t *entry=ehci.table+(ehci.slot_frame[i]&255)*4;
    /* Only replace the exact head installed by this worker. A foreign edit
     * makes ownership uncertain: retain every descriptor until reset. */
    if(V32(entry,0)!=((uintptr_t)&p->td[i]|4)) {
        ehci.bad_link=V32(entry,0); ehci.reason=0x5c; return 0;
    }
    V32(entry,0)=ehci.old_link[i]; barrier(); ehci.linked&=~(1u<<i); return 1;
}
static void ehci_stop(AudioPort *p,unsigned reason) {
    p->wanted=0; debug_ports[p-mx1_audio_ports].mode=0; barrier();
    if(reason) ehci.reason=reason;
    if(p->phase==2) {
        for(unsigned i=0;i<ENSLOT;i++) ehci_unlink(p,i);
        p->close_frame=ehci_frame(); p->phase=3; stage(p,ehci.reason?ehci.reason:0x57,0);
    }
}
static int ehci_arm(AudioPort *p,unsigned i) {
    unsigned now=ehci_frame(), distance=(p->next_frame-now)&2047;
    if(distance<4 || distance>64) { p->next_frame=(now+4)&2047; p->missed++; }
    unsigned f=p->next_frame, old=V32(ehci.table,(f&255)*4);
    if(!ehci_path(p,old)) return 0;
    IsoTD *t=&p->td[i]; uintptr_t data=(uintptr_t)t->pcm;
    zero(t,32);
    V32(t,0)=old; V32(t,4)=ehci.endpoint; V32(t,8)=ehci.mask;
    V32(t,16)=data; V32(t,20)=(data+183)&~4095u; V32(t,24)=1;
    V32(t,12)=0x80000080u|(184u<<16); /* IOC, active, 184-byte buffer */
    ehci.old_link[i]=old; ehci.slot_frame[i]=f;
    barrier(); V32(ehci.table,(f&255)*4)=(uintptr_t)t|4;
    ehci.linked|=1u<<i; p->next_frame=(f+1)&2047; return 1;
}
static void ehci_packet(AudioPort *p,unsigned i,unsigned status) {
    unsigned left=(status>>16)&1023,bytes=left<=184?184-left:0;
    ehci.status=status; ehci.last_status[i]=status; ehci.last_bytes=bytes;
    /* Missed uframes, split errors and active descriptors are never samples. */
    if((status&0xfc) || bytes<160 || bytes>184 || (bytes&3)) { p->malformed++; return; }
    unsigned w=p->write_count;
    if(w-p->read_count>=NPACKET) { p->overflow++; return; }
    Packet *q=&p->packets_in[w&(NPACKET-1)]; unsigned nonzero=0;
    for(unsigned j=0;j<bytes/2;j++) {
        int sample=p->td[i].pcm[j]; q->pcm[j]=(int16_t)sample;
        unsigned magnitude=sample<0?(unsigned)-sample:(unsigned)sample;
        if(magnitude>ehci.peak[j&1]) ehci.peak[j&1]=magnitude;
        nonzero|=magnitude;
    }
    if(nonzero) ehci.nonzero++;
    q->frames=bytes/4; barrier(); p->write_count=w+1; p->packets++;
}
static void ehci_service(unsigned event) {
    AudioPort *p=ehci.owner;
    if(!p || !p->phase || !ehci_current(p)) return;
    unsigned now=ehci_frame(),sts=V32(ehci.regs,4);
    ehci.events++;
    if(p->phase==2) {
        if(!p->wanted) ehci_stop(p,0);
        else if((event&16) || (sts&0x1010)) ehci_stop(p,0x59);
        else if((int32_t)(debug_ticks-ehci.deadline)>=0) ehci_stop(p,0x58);
        else if((uint32_t)(debug_ticks-ehci.serviced)>400 || U16((void*)0x4000bbb0,0)) ehci_stop(p,0x5a);
        else if((V32(ehci.regs,20)&~4095u)!=(uintptr_t)ehci.table) ehci_stop(p,0x5c);
    }
    ehci.serviced=debug_ticks;
    if(p->phase==2) for(unsigned n=0;n<ENSLOT;n++) {
        unsigned i=p->tail_slot,age=(now-ehci.slot_frame[i])&2047;
        if(age<2 || age>=1024) break;
        if(!ehci_unlink(p,i)) { ehci_stop(p,0x5c); break; }
        barrier(); ehci_packet(p,i,V32(&p->td[i],12));
        if(!ehci_arm(p,i)) { ehci_stop(p,0x5b); break; }
        p->tail_slot=(i+1)&15;
    }
    if(p->phase==3 && !ehci.linked &&
       ((sts&0x1000) || ((now-p->close_frame)&2047)>=2)) {
        /* No descriptor remained reachable for two complete H-frames. Stop
         * retains buffers if FRINDEX stops, links change, or reset is unclear. */
        p->phase=0; barrier(); p->claimed=0;
    }
    ehci_snapshot(p);
}
static int ehci_begin(AudioPort *p) {
    if(!p->wanted || p->phase || ehci.poll_pending || (ehci.owner && ehci.owner->claimed && ehci.owner!=p)) return -9;
    uint8_t *driver=PTR((void*)0x6002b0e8,4);
    if(!driver || !PTR(driver,0x40) || U16(p->dev,0x4a)!=1 || U16(p->dev,0x58)) return -5;
    p->controller=PTR(driver,0x40);
    zero(&ehci,sizeof ehci); ehci.owner=p; ehci.regs=PTR(p->controller,4);
    ehci.table=(uint8_t *)(uintptr_t)(V32(ehci.regs,20)&~4095u);
    DebugPort *d=&debug_ports[p-mx1_audio_ports];
    uint8_t *hub=PTR(p->dev,0xec), *parent=hub?PTR(hub,4):0;
    /* Only a directly attached full-speed device below the measured HS hub.
     * No nested full-speed hubs or guessed TT routing. */
    if(!hub || !parent || d->topology[4]!=(uintptr_t)hub || d->topology[5]!=(uintptr_t)parent ||
       d->topology[1]!=U16(p->dev,0x4c) || U16(parent,0x4a)!=1 || U16(parent,0x58)!=0x400 ||
       d->topology[7]!=U16(parent,0x4c) || d->topology[6]!=1 || d->topology[8]!=0x400 ||
       !d->topology[7] || d->topology[7]>127 || !d->topology[11] || d->topology[11]>7 ||
       PTR(hub,4+d->topology[11]*4)!=p->dev || !U16(p->dev,0x4c) || U16(p->dev,0x4c)>127) {
        stage(p,0x50,-5); ehci_snapshot(p); return -5;
    }
    ehci.endpoint=0x80000400u|U16(p->dev,0x4c)|(d->topology[7]<<16)|(d->topology[11]<<24);
    ehci.mask=0x1c01; /* SS u0, CS u2/u3/u4; one <=184-byte FS IN packet */
    unsigned cmd=V32(ehci.regs,0),sts=V32(ehci.regs,4);
    if((cmd&0x1f)!=0x19 || !(sts&0x4000) || (sts&0x1010) || ehci.table!=(void*)0x4000b000 ||
       V32(ehci.regs,16) || U16((void*)0x4000bbb0,0)) {
        stage(p,0x51,-5); ehci_snapshot(p); return -5;
    }
    /* The stock table shares its roots. Walk each distinct chain once, keeping
     * admission bounded instead of rescanning eight dummy iTDs 256 times. */
    uint32_t checked[16]; unsigned seen=0;
    for(unsigned f=0;f<256;f++) {
        unsigned link=V32(ehci.table,f*4),j=0;
        while(j<seen && checked[j]!=link) j++;
        if(j<seen) continue;
        if(seen==16 || !ehci_path(p,link)) {
            stage(p,0x52,-5); ehci_snapshot(p); return -5;
        }
        checked[seen++]=link;
    }
    p->write_count=p->read_count=p->quarter=p->primed=p->tail_slot=0;
    p->next_frame=(ehci_frame()+4)&2047; ehci.deadline=debug_ticks+240000; ehci.serviced=debug_ticks;
    zero(p->td,sizeof p->td);
    for(unsigned i=0;i<ENSLOT;i++) if(!ehci_arm(p,i)) {
        p->phase=2; ehci_stop(p,0x5b); return 0;
    }
    /* Audio can preempt this worker. Publish running only after all slots
     * are initialized, so a converter failure cannot interrupt construction. */
    barrier(); p->phase=2;
    stage(p,0x56,0); ehci_snapshot(p); return 0;
}
static void ehci_poll_done(unsigned controller,unsigned status,uintptr_t token) {
    (void)status;(void)token;
    ehci.poll_pending=0; barrier();
    if(controller==1) ehci_service(0);
}
static void ehci_tick(void) {
    AudioPort *p=ehci.owner;
    if(!p || !p->phase || !p->controller || ehci.poll_pending || (debug_ticks&31)) return;
    /* Original 03000020 controller-status queue and callback ABI. One queued
     * request maximum, every eight ms as fallback; no USB endpoint lifetime. */
    ehci.poll_pending=1; barrier();
    if(FN(0x6000c377,int(*)(unsigned,void*,uintptr_t))(1,(void*)ehci_poll_done,0)) ehci.poll_pending=0;
}
int mx1_ehci_request(void *dev,void *ep,unsigned flags,unsigned a,unsigned b,void *buf,unsigned len,void *callback,uintptr_t token) {
    AudioPort *p=for_device(dev);
    if(callback==(void*)debug_done) {
        if(!p || ep!=p->ep || p->phase!=2 || (token&3)!=(unsigned)(p-mx1_audio_ports) ||
           (token>>2)!=(p->generation&0x3fffffff)) return -9;
        ehci_service(0); ehci_snapshot(p); debug_done(dev,ep,0,0,token); return 0;
    }
    if(p && ep==p->ep && callback==(void*)start_done && token==(uintptr_t)p) {
        int result=ehci_begin(p);
        if(!result) start_done(dev,ep,0,0,token);
        return result;
    }
    /* This experiment does not implement a shared TT bandwidth allocator.
     * A concurrent new periodic request gets stock bandwidth-unavailable -13
     * while we retire; never run an unbudgeted second FS periodic endpoint. */
    if(ehci.owner && ehci.owner->phase && (((uint8_t*)ep)[10]==1 || ((uint8_t*)ep)[10]==3)) {
        ehci_stop(ehci.owner,0x5a); return -13;
    }
    return FN(0x600111ef,int(*)(void*,void*,unsigned,unsigned,unsigned,void*,unsigned,void*,uintptr_t))
        (dev,ep,flags,a,b,buf,len,callback,token);
}
int mx1_ehci_cancel(void *dev,void *ep) {
    AudioPort *p=for_device(dev);
    if(p && p==ehci.owner && ep==p->ep && diagnostic(p)->controller==1) { ehci_stop(p,0); return 0; }
    return FN(0x600113af,int(*)(void*,void*))(dev,ep);
}
int mx1_ehci_event(unsigned controller,unsigned event) {
    if(controller==1) ehci_service(event);
    return FN(0x60011be5,int(*)(unsigned,unsigned))(controller,event);
}
int mx1_ehci_reset(unsigned controller,unsigned operation) {
    AudioPort *p=ehci.owner; uint8_t *regs=0;
    if(controller==1 && p && p->phase && ehci_current(p)) { regs=ehci.regs; ehci_stop(p,0x59); }
    int result=FN(0x600107f7,int(*)(unsigned,unsigned))(controller,operation);
    if(regs && operation==2) {
        /* Stock teardown may free its context even on an error. MMIO is
         * independent of that allocation; release only when halted. */
        p->controller=0; p->wanted=0;
        if(V32(regs,4)&0x1000) { p->phase=0; ehci.linked=0; barrier(); p->claimed=0; }
        else p->phase=4; /* quarantined until reboot */
    }
    return result;
}
extern void host_ehci_bind_original(unsigned,void*);
void mx1_ehci_bind(unsigned controller,uint8_t *driver) {
    host_ehci_bind_original(controller,driver);
    U32(driver,8)=(uintptr_t)mx1_ehci_reset;
    U32(driver,12)=(uintptr_t)mx1_ehci_request;
    U32(driver,16)=(uintptr_t)mx1_ehci_cancel;
    U32(driver,0x2c)=(uintptr_t)mx1_ehci_event;
}
