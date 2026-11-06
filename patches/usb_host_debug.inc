/* Development bridge protocol v1. F0 7D 44 42 01 01 seq op [u32 septets]
 * checksum F7. Sum of bytes 1..checksum is zero modulo 128. Replies op|40.
 * Only the measured FM1's current MIDI endpoint can access this interface.
 * No arbitrary memory access, flash operation or USB reset is exposed. */
static int debug_match(unsigned port,void *ep) {
    if(port>=4 || !ep || !debug_ports[port].dev) return 0;
    return PTR(PTR(ep,0x20),8)==debug_ports[port].dev;
}
static void debug_reply(DebugPort *d,unsigned seq,unsigned op,const uint32_t *v,unsigned count) {
    uint8_t *b=d->reply; unsigned n=8,sum=0;
    b[0]=0xf0;b[1]=0x7d;b[2]=0x44;b[3]=0x42;b[4]=1;b[5]=1;b[6]=seq;b[7]=op|64;
    for(unsigned i=0;i<count;i++) for(unsigned j=0;j<5;j++) b[n++]=(v[i]>>(j*7))&127;
    for(unsigned i=1;i<n;i++) sum+=b[i];
    b[n++]=(-sum)&127;b[n++]=0xf7;
    d->reply_pos=0; barrier(); d->reply_n=n;
    debug_wake_tx();
}
static void debug_capture(AudioPort *p) {
    DebugPort *d=&debug_ports[p-mx1_audio_ports];
    uint8_t *regs=PTR(p->controller,8),*hcca=PTR(p->controller,12);
    static const uint8_t offsets[]={0,4,8,12,16,24,28,48,52,56,60,64,68};
    d->snapshot_seq++; barrier();
    unsigned n=0;
    d->raw[n++]=(uintptr_t)p->controller; d->raw[n++]=(uintptr_t)&p->ed; d->raw[n++]=(uintptr_t)p->td;
    for(unsigned i=0;i<sizeof offsets;i++) d->raw[n++]=V32(regs,offsets[i]);
    d->raw[n++]=V32(hcca,0x80); d->raw[n++]=V32(hcca,0x84);
    d->raw[n++]=p->ed.control; d->raw[n++]=p->ed.tail; d->raw[n++]=p->ed.head; d->raw[n++]=p->ed.next;
    uintptr_t head=p->ed.head&~31u,base=(uintptr_t)p->td;
    int valid=head>=base && head<base+sizeof p->td && (head-base)%sizeof(IsoTD)==0;
    for(unsigned i=0;i<8;i++) d->raw[n++]=valid?V32((void*)head,i*4):0;
    d->raw[n++]=U32(p->controller,0x28); d->raw[n++]=U32(p->controller,0x2c);
    d->raw[n++]=U32(p->controller,0x30); d->raw[n++]=U32(p->controller,0x34);
    d->raw[n++]=U16(p->controller,0x38); d->raw[n++]=U32(p->controller,0x53c);
    for(unsigned i=0;i<NTD;i++) { d->raw[n++]=p->td[i].control; d->raw[n++]=p->td[i].psw[0]; }
    for(unsigned i=0;i<32;i++) d->raw[n++]=V32(hcca,i*4);
    barrier(); d->snapshot_seq++;
}
static void debug_done(void *dev,void *ep,unsigned bytes,int status,uintptr_t token) {
    (void)ep;(void)bytes;
    unsigned port=token&3; AudioPort *p=&mx1_audio_ports[port]; DebugPort *d=&debug_ports[port];
    if(!d->busy || d->dev!=dev || (token>>2)!=(p->generation&0x3fffffff)) return;
    uint32_t v[]={status?(status<0?(unsigned)-status:(unsigned)status):0,d->snapshot_seq};
    debug_reply(d,d->sequence,4,v,2); barrier(); d->busy=0;
}
/* App-manager event 5 with a private marker. RX only queues this intent;
 * synchronous control/lookup APIs must never run inside the MIDI RX task.
 * No ISO submission, descriptor edits or controller register writes here. */
static void debug_probe(uint8_t *event) {
    uint8_t *dev=PTR(event,4),*r=record(dev);
    if(!r || !(r[0]&1) || U32(r,4) || U16(r,2)>=4) return;
    unsigned port=U16(r,2); DebugPort *d=&debug_ports[port]; AudioPort *p=&mx1_audio_ports[port];
    unsigned op=d->probe;
    if(d->dev!=dev || !op || op>4 || p->claimed || U16(dev,0x4a)!=1) return;
    int e=-5; stage(p,0x30+op,0);
    if(op==1) {
        e=FN(0x60009559,int(*)(void*,unsigned,unsigned,unsigned,unsigned,unsigned,void*,unsigned))
            (dev,0x22,1,0x100,0x84,3,(void*)fm1_rate,0);
    } else if(op==2 || op==4) {
        e=FN(0x60009559,int(*)(void*,unsigned,unsigned,unsigned,unsigned,unsigned,void*,unsigned))
            (dev,1,11,op==2,1,0,0,0);
    } else {
        /* Resolve after the rebind event has populated the manager record. */
        for(unsigned i=0;i<U16(r,0x20) && i<8;i++) {
            uint8_t *n=PTR(r,0x28+i*8),*ep=0;
            if(!n || n[0x13]!=1 || n[0x14]!=1 || n[0x15]!=1) continue;
            e=FN(0x600096c7,int(*)(void*,int,int,int,int,int,void*))(n,0,128,1,0,0,&ep);
            if(!e && (!ep || ep[8]!=0x84 || ep[9]!=128 || ep[10]!=1 || U16(ep,0x10)!=184)) e=-5;
            break;
        }
    }
    d->probe_result=(uint32_t)e; d->probe_done=op;
    stage(p,0x38+op,e); barrier(); d->probe=0;
}
extern void mx1_host_debug_state(unsigned,uint32_t *);
static void debug_command(unsigned port) {
    DebugPort *d=&debug_ports[port]; AudioPort *p=&mx1_audio_ports[port]; AudioDiagnostic *a=diagnostic(p);
    uint8_t *b=d->input; unsigned n=d->input_n,op=b[7],seq=b[6],sum=0;
    if((n!=10 && n!=15) || b[3]!=0x42 || b[4]!=1 || b[5]!=1 || b[n-1]!=0xf7) { d->errors++; return; }
    for(unsigned i=1;i<n-1;i++) { if(b[i]&128) { d->errors++; return; } sum+=b[i]; }
    if((sum&127) || (n==15 && b[12]>15)) { d->errors++; return; }
    if(d->reply_n || d->busy) { d->dropped++; return; }
    uint32_t arg=0,v[40]; unsigned k=1; v[0]=0;
    if(n==15) for(unsigned j=0;j<5;j++) arg|=(uint32_t)b[8+j]<<(7*j);
    if(op==1 && n==10) {
        uint32_t fields[]={0xb3,port,a->stage,a->result,a->controller,p->phase,a->control,a->flags,a->cc,a->frame,
            p->packets,p->malformed,p->overflow,p->underrun,p->missed,p->dsp_errors,p->wanted,p->claimed,p->generation,
            p->write_count,p->read_count,p->next_frame,p->close_frame,p->cost,p->tail_slot,d->mode,d->errors,d->dropped,
            d->probe,d->probe_done,d->probe_result};
        for(unsigned i=0;i<sizeof fields/sizeof fields[0];i++) v[k++]=fields[i];
    } else if(op==2 && n==15 && arg==3) {
        v[k++]=arg;
        for(unsigned i=0;i<12;i++) v[k++]=d->topology[i];
    } else if(op==2 && n==15 && arg==4) {
        v[k++]=arg; mx1_host_debug_state(port,v+k); k+=24;
    } else if(op==2 && n==15 && arg<3) {
        unsigned s=d->snapshot_seq;
        if(!s || (s&1)) v[0]=2;
        else {
            unsigned off=arg==0?0:arg==1?36:70,count=arg==0?36:arg==1?34:32;
            v[k++]=arg; v[k++]=s;
            for(unsigned i=0;i<count;i++) v[k++]=d->raw[off+i];
            barrier(); if(s!=d->snapshot_seq) { v[0]=2;k=1; }
        }
    } else if(op==3 && n==15 && arg<=2) {
        if(p->phase!=2 || !p->claimed || !p->wanted) v[0]=2;
        else { d->mode_until=debug_ticks+240000; barrier(); d->mode=arg; v[k++]=arg; }
    } else if(op==4 && n==10) {
        if(p->phase!=2 || !p->claimed || !p->wanted) v[0]=2;
        else {
            d->sequence=seq; d->busy=1; barrier();
            uintptr_t token=(p->generation<<2)|port;
            int result=FN(0x6000c277,int(*)(void*,void*,unsigned,unsigned,unsigned,void*,unsigned,void*,uintptr_t,unsigned))
                (p->dev,p->ep,0,0,0,0,0,(void*)debug_done,token,0);
            if(result) debug_done(p->dev,p->ep,0,result,token);
            return;
        }
    } else if(op==5 && n==15 && arg>=1 && arg<=4) {
        if(a->controller!=1 || p->claimed || d->probe) v[0]=2;
        else {
            uint32_t event[3]={5,(uintptr_t)d->dev,0x3242444d};
            d->probe=arg; barrier();
            if(!FN(0x60007e11,int(*)(void*))(event)) { d->probe=0;v[0]=3; }
            else v[k++]=arg; /* accepted, completion is in status */
        }
    } else v[0]=1;
    debug_reply(d,seq,op,v,k);
}
int mx1_debug_receive(unsigned port,void *ep,uint32_t word) {
    if(!debug_match(port,ep) || (word&0xf0)) return 0;
    DebugPort *d=&debug_ports[port]; unsigned cin=word&15;
    if(word==0x447df004) { /* fresh command also resynchronizes a truncated one */
        if(d->input_n) d->errors++;
        d->input[0]=0xf0;d->input[1]=0x7d;d->input[2]=0x44;d->input_n=3; return 1;
    }
    if(!d->input_n) return 0;
    if(cin==15 && (word>>8&255)>=0xf8) return 0; /* stock sync boundary still applies */
    if(cin<4 || cin>7) { d->input_n=0;d->errors++;return 0; }
    if(d->input_n>sizeof d->input) { if(cin!=4) d->input_n=0; return 1; }
    unsigned n=cin==4?3:cin-4;
    for(unsigned i=0;i<n;i++) {
        uint8_t b=word>>(8+i*8);
        if(d->input_n>=sizeof d->input || (b&128 && !(b==0xf7 && i+1==n && cin!=4))) {
            d->input_n=cin==4?sizeof d->input+1:0;d->errors++;return 1;
        }
        d->input[d->input_n++]=b;
    }
    if(cin!=4) { debug_command(port); d->input_n=0; }
    return 1;
}
unsigned mx1_debug_transmit(unsigned port,void *ep,uint32_t *out) {
    if(!debug_match(port,ep) || diagnostics[port].sysex) return 0;
    DebugPort *d=&debug_ports[port]; unsigned n=d->reply_n,k=0,pos=d->reply_pos;
    barrier();
    if(!n) {
        /* The audio task wakes TX every 4096 calls, even without a claimed
         * audio stream or musical traffic. Coalesce missed intervals. */
        if((uint32_t)(debug_ticks-d->heartbeat)<4096) return 0;
        d->heartbeat=debug_ticks;
        uint32_t m[24]; mx1_host_debug_state(port,m);
        uint32_t v[]={0,0xb3,diagnostics[port].stage,m[1]|(m[2]<<1)|(m[7]<<8),
            m[11]|(m[12]<<1)|(m[17]<<8),m[3],m[13]};
        volatile uint8_t b[45];
        b[0]=0xf0;b[1]=0x7d;b[2]=0x44;b[3]=0x42;b[4]=1;b[5]=1;b[6]=0;b[7]=0x7e;
        unsigned sum=0;
        for(unsigned i=0;i<7;i++) for(unsigned j=0;j<5;j++) b[8+i*5+j]=(v[i]>>(j*7))&127;
        for(unsigned i=1;i<43;i++) sum+=b[i];
        b[43]=(-sum)&127; b[44]=0xf7;
        for(unsigned i=0;i<15;i++) out[i]=(i==14?7:4)|((uint32_t)b[i*3]<<8)|
            ((uint32_t)b[i*3+1]<<16)|((uint32_t)b[i*3+2]<<24);
        return 15;
    }
    while(pos<n && k<16) {
        unsigned take=n-pos; if(take>3) take=3;
        uint32_t w=pos+take==n?4+take:4;
        for(unsigned i=0;i<take;i++) w|=(uint32_t)d->reply[pos++]<<(8+i*8);
        out[k++]=w;
    }
    d->reply_pos=pos;
    if(pos==n) { d->heartbeat=debug_ticks; barrier(); d->reply_n=0; }
    return k;
}
