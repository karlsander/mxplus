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
        uint32_t fields[]={0xb1,port,a->stage,a->result,a->controller,p->phase,a->control,a->flags,a->cc,a->frame,
            p->packets,p->malformed,p->overflow,p->underrun,p->missed,p->dsp_errors,p->wanted,p->claimed,p->generation,
            p->write_count,p->read_count,p->next_frame,p->close_frame,p->cost,p->tail_slot,d->mode,d->errors,d->dropped};
        for(unsigned i=0;i<sizeof fields/sizeof fields[0];i++) v[k++]=fields[i];
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
    while(pos<n && k<16) {
        unsigned take=n-pos; if(take>3) take=3;
        uint32_t w=pos+take==n?4+take:4;
        for(unsigned i=0;i<take;i++) w|=(uint32_t)d->reply[pos++]<<(8+i*8);
        out[k++]=w;
    }
    d->reply_pos=pos; barrier(); if(pos==n) d->reply_n=0;
    return k;
}
