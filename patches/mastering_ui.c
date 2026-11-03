/* MX-1 mastering surface, independently written 2026-11-03.
 * Control-task code only. Stock parameter transactions own DSP notification.
 * See docs/MASTERING.md for address/ABI evidence and offline boundaries. */
#pragma clang section text=".master_text" rodata=".master_rodata" bss=".master_state"
typedef unsigned char u8;
typedef unsigned short u16;
typedef unsigned int u32;
#define FN(a,t) ((t)(a))
#define MASTER ((void *)0x600b53b8u)
#define MIX ((void *)0x600b53acu)
#define SETUP ((void *)0x60514504u)
#define CONTEXT ((void *)0x605141ccu)
#define KEYS ((volatile u8 *)0x605129a4u)
#define ANALOG ((volatile u16 *)0x605129b4u)
#define DIRTY (*(volatile u16 *)0x605141ccu)
#define MASTER_KEY 0x17u
#define HOLD_TICKS 1200u
extern void mx1_route_ui_event(const u8 *event);
extern void mx1_master_redraw_original(void *context);

/* Each entry is a zero-based hidden EQ index, or -1. Odd ADC IDs are
 * faders, even IDs are the TONE/FILTER knobs above them. */
static const signed char assignments[28] = {
    -1,-1,-1,-1,-1,-1, 1,16, -1,-1, 4,3, 2,5, 7,6,
    -1,8, 10,9, -1,11, 14,13, 12,15, -1,-1
};
static const char labels[17][4] = {
    "EQ "," In","Lty","Lgn","LFr","L Q","LMg","LMf","LMq",
    "HMg","HMf","HMq","Hty","Hgn","HFr","H Q","Out"
};
struct master_state {
    u32 started, acquired, restore;
    u16 before[28], last[28];
    u8 swallowed[11];
    u8 active, pending, selected, redraw;
};
struct master_state mx1_master_state;
#define S mx1_master_state
static int get(void *ctx, unsigned id, unsigned addr) {
    return FN(addr,int (*)(void *,unsigned,unsigned))(ctx,id,0);
}
static void set(void *ctx, unsigned id, int value) {
    FN(0x600161f7u,void (*)(void *,unsigned,int,unsigned))(ctx,id,value,0);
}
static u32 now(void) {
    u32 ticks[2];
    FN(0x010037e9u,void (*)(u32 *))(ticks);
    return ticks[1];
}
static int eligible(void) {
    unsigned page = *(volatile u16 *)0x600b4b5eu;
    return *(volatile u32 *)0x600b4b94u == 0 && !*(volatile u32 *)0x600b537cu &&
        (page == 5 || page == 15) &&
        !FN(0x60018259u,int (*)(void *))((void *)0x605144ccu);
}
static int no_keys(void) {
    for (unsigned i=0;i<11;++i) if (KEYS[i]) return 0;
    return 1;
}
static void led(unsigned id,unsigned mode) {
    FN(0x60014a79u,void (*)(unsigned,unsigned,unsigned))(id,mode,9);
}
static int eq(unsigned id) { return get(MASTER,id,0x6001fa49u); }
static unsigned maximum(unsigned id) {
    return ((const u32 *)0x600686d8u)[(0x476u+id)*4u+1u];
}
static unsigned scaled(unsigned id,unsigned raw) {
    return (raw*maximum(id)+63u)/127u;
}
static int crossed(int before,int after,int target) {
    return (before <= target && after >= target) || (before >= target && after <= target);
}
/* Query current logical mixer targets, never replace them with physical
 * positions just because the edit surface used those controls. */
static int target(unsigned adc) {
    if (adc >= 6) {
        unsigned strip=(adc-6)/2;
        return get(MIX,strip+((adc&1)?0x58:0x63),0x6001e65fu);
    }
    if (adc == 5) return get(MIX,0xe2,0x6001e65fu);
    return get(SETUP,0x1e + adc,0x6001a1cfu);
}
static int linked_follower(unsigned adc) {
    if (adc != 8 && adc != 9 && adc != 12 && adc != 13) return 0;
    return get((void *)0x600b5390u,adc<10?3:4,0x6001a897u) == 1;
}
static void clear_stock_pickup(unsigned adc) {
    if (adc>=6) set(SETUP,(adc-6)/2+((adc&1)?0x2d:0x38),-1);
}
static void enter(void) {
    S.pending=0; S.active=1; S.selected=0; S.acquired=0; S.restore=0;
    for (unsigned i=0;i<28;++i) {
        S.last[i]=ANALOG[i*4]; S.before[i]=(u16)target(i);
    }
    FN(0x60014a19u,void (*)(void))();
    S.redraw=1; DIRTY=0xffff;
}
static void leave(void) {
    S.active=0; S.pending=0; S.restore=0;
    for (unsigned i=0;i<28;++i) {
        /* Channel targets may have changed through MIDI during editing. */
        int wanted=i>=5?target(i):S.before[i];
        S.before[i]=(u16)wanted;
        if (S.last[i] != wanted && !linked_follower(i)) S.restore|=1u<<i;
        if (i>=6) set(SETUP,(i-6)/2+((i&1)?0x2d:0x38),
                        S.restore&(1u<<i)?S.last[i]:-1);
    }
    DIRTY=0xffff;
    mx1_master_redraw_original(CONTEXT);
}
__attribute__((section(".master_head")))
void mx1_master_redraw(void *context) {
    if (!S.active) { mx1_master_redraw_original(context); return; }
    led(6,3); /* Stock MASTERING blink mode. */
    led(0x19,eq(0)?1:0);
    for (unsigned strip=0;strip<11;++strip) {
        unsigned adc=7+2*strip;
        led(0x29+strip,assignments[adc]<0?0:(S.acquired&(1u<<adc)?1:3));
    }
    char value[16]={0};
    FN(0x6001faddu,void (*)(void *,char *,unsigned,int))(MASTER,value,S.selected,eq(S.selected));
    for (unsigned i=0;i<4;++i) if (!value[i]) {
        for (;i<4;++i) value[i]=' ';
        break;
    }
    FN(0x60054f85u,void (*)(void *,unsigned,const char *,unsigned))
        ((void *)0x60512984u,0,labels[S.selected],0);
    FN(0x60054f85u,void (*)(void *,unsigned,const char *,unsigned))
        ((void *)0x60512984u,1,value,0);
    DIRTY=0; S.redraw=0;
}
void mx1_master_tick(void) {
    /* Preserve the registered stock periodic callback and queue drain. */
    FN(0x60010b77u,void (*)(void))();
    if (S.pending && (!eligible() || !no_keys())) {
        /* Pending gesture must never take over a newly opened modal/page. */
        S.pending=0;
    }
    if (S.pending && (u32)(now()-S.started)>=HOLD_TICKS) enter();
    if (S.active && !eligible()) leave();
    if (S.active && S.redraw) mx1_master_redraw(CONTEXT);
}
void mx1_master_ui_event(const u8 *event) {
    unsigned type=event[0],id=event[1];
    int key=type>=1 && type<=3 && id<0x55;
    unsigned bit=1u<<(id&7);
    if (S.active && !eligible()) leave();
    /* Releases for controls pressed in the editor cannot leak into Roland's
     * release-only actions after exiting. Auto-repeat is also consumed. */
    if (key && !S.active && (S.swallowed[id/8]&bit) && type!=2) {
        if (type==1) S.swallowed[id/8]&=(u8)~bit;
        if (!(id==MASTER_KEY && S.pending)) return;
    }
    if (S.pending) {
        if (key && id==MASTER_KEY && type==1) {
            S.pending=0;
            const u8 down[4]={2,MASTER_KEY,0,0};
            mx1_route_ui_event(down); mx1_route_ui_event(event); return;
        }
        if (key && id==MASTER_KEY) return;
        /* Retain stock MASTERING+encoder gestures, without a delayed entry. */
        S.pending=0; S.swallowed[MASTER_KEY/8]&=(u8)~(1u<<(MASTER_KEY&7));
        const u8 down[4]={2,MASTER_KEY,0,0};
        mx1_route_ui_event(down);
    }
    if (!S.active && key && type==2 && id==MASTER_KEY && eligible() && no_keys()) {
        S.pending=1; S.started=now(); S.swallowed[id/8]|=bit; return;
    }
    if (S.active) {
        if (key) {
            if (type==2) {
                int already=S.swallowed[id/8]&bit;
                S.swallowed[id/8]|=bit;
                if (!already && id==MASTER_KEY) { leave(); return; }
                if (!already && id==1) { set(MASTER,0,!eq(0)); S.selected=0; S.redraw=1; }
            } else if (type==1) S.swallowed[id/8]&=(u8)~bit;
        } else if (type==0xb && id<28) {
            unsigned raw=event[2]|((unsigned)event[3]<<8);
            if (raw<=127) {
                unsigned old=S.last[id]; S.last[id]=(u16)raw;
                ANALOG[id*4]=(u16)raw;
                int parameter=assignments[id];
                if (parameter>=0) {
                    unsigned value=scaled((unsigned)parameter,raw);
                    S.selected=(u8)parameter; S.redraw=1;
                    if (crossed((int)scaled((unsigned)parameter,old),(int)value,eq((unsigned)parameter)))
                        S.acquired|=1u<<id;
                    if (S.acquired&(1u<<id)) set(MASTER,(unsigned)parameter,(int)value);
                }
            }
        }
        if (S.redraw) mx1_master_redraw(CONTEXT);
        /* Only surface controls are taken over. Non-control notifications
         * still traverse the original queue/dispatcher. */
        if (key || type==4 || type==5 || type==0xb) return;
    }
    if (!S.active && type==0xb && id<28 && (S.restore&(1u<<id))) {
        unsigned raw=event[2]|((unsigned)event[3]<<8);
        if (raw>127) return;
        unsigned old=S.last[id]; S.last[id]=(u16)raw; ANALOG[id*4]=(u16)raw;
        int wanted=id>=5?target(id):S.before[id];
        if (!linked_follower(id) && !crossed((int)old,(int)raw,wanted)) {
            DIRTY|=8; mx1_master_redraw_original(CONTEXT); return;
        }
        S.restore&=~(1u<<id); clear_stock_pickup(id);
    }
    mx1_route_ui_event(event);
}
