/* Control-task display diagnostics, independently written 2026-11-04.
 * Observe the existing mastering dispatcher and main-side host status only.
 * No USB/DMA access, MIDI injection, parameter writes or new task. */
#pragma clang section text=".diag_text" rodata=".diag_rodata" bss=".diag_state"
typedef unsigned char u8;
typedef unsigned short u16;
typedef unsigned int u32;
#define FN(a,t) ((t)(a))
#define KEYS ((volatile u8 *)0x605129a4u)
#define MASTER_STATE ((volatile u8 *)0x01017444u)
#define DIRTY (*(volatile u16 *)0x605141ccu)
extern void mx1_master_ui_event(const u8 *);
extern void mx1_master_tick(void);
extern void mx1_master_redraw(void *);
struct snapshot { u16 guard, page, first, high; };
struct diagnostic_state {
    struct snapshot master, tap;
    u16 press, count, cancel, master_after, tap_before, tap_after, cached;
    u8 active, page, select, swallow, valid, spare;
};
struct diagnostic_state mx1_diag_state;
#define D mx1_diag_state
static unsigned state(void) { return MASTER_STATE[135] | ((unsigned)MASTER_STATE[136]<<1); }
static void snapshot(struct snapshot *s) {
    unsigned page=*(volatile u16 *)0x600b4b5eu, first=0xffff;
    for (unsigned i=0;i<88;++i) if (KEYS[i/8] & (1u<<(i&7))) { first=i; break; }
    s->guard=(*(volatile u32 *)0x600b4b94u!=0) |
        ((*(volatile u32 *)0x600b537cu!=0)<<1) |
        ((!((page>=5 && page<=10) || page==15))<<2) |
        ((FN(0x60018259u,int (*)(void *))((void *)0x605144ccu)!=0)<<3) |
        ((first!=0xffff)<<4);
    s->page=(u16)page; s->first=(u16)first; s->high=KEYS[10];
}
static const char labels[][3]={
    "bLd","btn","Cnt","Mgd","MPg","MKy","MHi","MSt",
    "tgd","tKy","tPr","tPo","CAn","StA","U1 ","U2 ","U3 ","U4 ",
    "C1 ","C2 ","C3 ","C4 "
};
static void render(void) {
    if (!D.active) return;
    unsigned p=D.page, value;
    if (p==0) value=0xd001;
    else if (p==1) value=D.press;
    else if (p==2) value=D.count;
    else if (p==3) value=D.master.guard;
    else if (p==4) value=D.master.page;
    else if (p==5) value=D.master.first;
    else if (p==6) value=D.master.high;
    else if (p==7) value=D.master_after;
    else if (p==8) value=D.tap.guard;
    else if (p==9) value=D.tap.first;
    else if (p==10) value=D.tap_before;
    else if (p==11) value=D.tap_after;
    else if (p==12) value=D.cancel;
    else if (p==13) value=state();
    else if (p<18) value=((volatile u8 *)0x600b1b3au)[p-14];
    else {
        unsigned port=p-18;
        volatile u8 *gates=(volatile u8 *)0x200003fcu;
        value=((unsigned)gates[port]<<8) | gates[port+5];
    }
    if (D.valid && D.cached==value) return;
    D.cached=(u16)value; D.valid=1;
    char hex[4];
    for (unsigned i=0;i<4;++i) hex[3-i]="0123456789AbCdEF"[(value>>(4*i))&15];
    FN(0x60054f85u,void (*)(void *,unsigned,const char *,unsigned))((void *)0x60512984u,0,labels[p],0);
    FN(0x60054f85u,void (*)(void *,unsigned,const char *,unsigned))((void *)0x60512984u,1,hex,0);
}
void mx1_diag_redraw(void *context) {
    mx1_master_redraw(context);
    D.valid=0; render();
}
void mx1_diag_tick(void) {
    unsigned before=state();
    mx1_master_tick();
    if ((before&2) && !(state()&3)) D.cancel=0xfffe; /* Periodic cancellation. */
    render();
}
void mx1_diag_event(const u8 *e) {
    unsigned type=e[0], id=e[1];
    if (id==0x29 && (type==1 || type==2)) D.select=(u8)(type==2);
    if (id==0 && type>=1 && type<=3 && D.swallow) {
        if (type==1) D.swallow=0;
        return;
    }
    /* Known SELECT path, independent of MASTERING's page/modal/lock/key guard.
     * Do not enter from boot/setup or an active mastering editor. */
    if (type==2 && id==0 && D.select && !*(volatile u32 *)0x600b4b94u &&
        (D.active || !(state()&1))) {
        D.active^=1; D.page=0; D.valid=0; D.swallow=1;
        DIRTY=0xffff;
        mx1_diag_redraw((void *)0x605141ccu);
        return;
    }
    if (D.active && (type==4 || type==5) && id==1) {
        int delta=(short)(e[2] | ((unsigned)e[3]<<8));
        if (delta) D.page=(u8)((D.page+(delta>0?1:21))%22);
        D.valid=0; render(); return;
    }
    unsigned before=state();
    if (type==2) {
        D.press=(u16)((type<<8)|id); ++D.count;
        if (id==0x17) snapshot(&D.master);
        if (id==0) { snapshot(&D.tap); D.tap_before=(u16)before; }
    }
    mx1_master_ui_event(e);
    unsigned after=state();
    if (type==2 && id==0x17) D.master_after=(u16)after;
    if (type==2 && id==0) D.tap_after=(u16)after;
    if ((before&2) && !(after&3) && !(type==1 && id==0x17))
        D.cancel=(u16)((type<<8)|id);
    if ((type>=1 && type<=5) || (after&1)) D.valid=0;
    render();
}
