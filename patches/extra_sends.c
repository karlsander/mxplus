/* Independent send controls and stock-slot policy. No sample IRQ work.
 * All DSP writes run on the original parameter task, after its queue drains. */
#pragma clang section text=".sends_text" rodata=".sends_rodata" bss=".sends_state"
typedef unsigned char u8;
typedef unsigned int u32;
#define FN(a,t) ((t)(a))
#define SLOT (*(volatile u32 *)0x600ccdbcu)
#define ALGO1 (*(volatile u32 *)0x600cce20u)
#define ONE 0x3f800000u
#define DEFAULT_CONFIG ((64u<<5)|(10u<<12))
struct sends_state {
    volatile u8 alt[11], fx[11], held[4];
    volatile u32 config;
    u32 applied;
    u8 valid, phones;
};
struct sends_state mx1_sends_state;
#define S mx1_sends_state
#include "extra_sends_data.h"

static u32 config(void) { return S.config ? S.config-1 : DEFAULT_CONFIG; }
static u32 parameter(unsigned id) {
    return FN(0x6001a897u,u32 (*)(u32,u32,u32))(0x600b5390,id,0);
}
static int blocked(void) {
    return *(volatile u32 *)0x6051deb8u>3 || parameter(0x19)==2;
}
static unsigned clamp(int value,unsigned maximum) {
    return value<0?0:(unsigned)value>maximum?maximum:(unsigned)value;
}
void mx1_sends_press(unsigned strip,unsigned page) { S.held[page]=(u8)(strip+1); }
void mx1_sends_release(unsigned page) { S.held[page]=0; }
void mx1_sends_adjust(unsigned strip,unsigned page,int delta) {
    if (strip>=11 || page>=3 || !delta || blocked()) return;
    delta=delta>0?1:-1;
    unsigned held=S.held[page]==strip+1;
    u32 cfg=config();
    if (page<2 && !held) {
        volatile u8 *level=page?&S.fx[strip]:&S.alt[strip];
        *level=(u8)clamp((int)*level+delta,127);
    } else {
        unsigned shift=page==0?0:page==1?2:held?12:5;
        unsigned maximum=page==0?2:page==1?7:127;
        unsigned mask=page==0?3:maximum;
        unsigned value=clamp((int)((cfg>>shift)&mask)+delta,maximum);
        cfg=(cfg&~(mask<<shift))|(value<<shift);
        S.config=cfg+1;
    }
    FN(0x0100e267u,void (*)(u32,u32))(0x6051dea8,8);
}
void mx1_sends_label(unsigned strip,unsigned page,char *label) {
    const char *text=0;
    unsigned value=0;
    u32 cfg=config();
    unsigned held=S.held[page]==strip+1;
    static const char modes[3][4]={{'O','F','F',' '},{'S','n','d','r'},{'P','h','o','n'}};
    static const char types[8][4]={{'S','t','E','r'},{'P','A','n',' '},{'C','r','o','S'},
        {'S','t','P','n'},{'S','P','r','L'},{'r','o','o','M'},{'H','A','L','L'},{'r','M','o','d'}};
    if (blocked()) text="modE";
    else if (page==3) text="----";
    else if (page==0 && held) text=modes[cfg&3];
    else if (page==1 && held) text=types[(cfg>>2)&7];
    else {
        label[0]=page==0?'A':page==1?'F':held?'t':'P';
        value=page==0?S.alt[strip]:page==1?S.fx[strip]:(cfg>>(held?12:5))&127;
    }
    if (text) { for (unsigned i=0;i<4;++i) label[i]=text[i]; return; }
    label[1]=(char)('0'+value/100);
    label[2]=(char)('0'+value/10%10);
    label[3]=(char)('0'+value%10);
}
static void coefficient(unsigned index,u32 bits) {
    FN(0x0100b5ebu,void (*)(u32,u32,u32,u32,u32))
        (0x20000b24,1,index,bits,0);
}
static void barrier(void) { FN(0x60054c15u,void (*)(u32))(0x20000b24); }
__attribute__((used,noinline)) static void graph_stopped(void *context) {
    S.valid=0;
    const u32 *graph=*(const u32 *const *)context;
    if (graph[1]!=0x600777c4u) return;
    /* The original stop has already run. Clear normal-graph validity before
     * initial passthrough slots are installed, without touching diagnostics. */
    coefficient(0x99,0); coefficient(0x9a,0); barrier();
}
__attribute__((naked)) void mx1_sends_graph(void) {
    __asm__ volatile("push {r4-r6, lr}\nmov r4, r0\nldr r3, =0x60026793\nblx r3\n"
                     "mov r0, r4\nbl graph_stopped\nldr pc, =0x600267bd\n");
}
__attribute__((naked)) static void original_load(void) {
    __asm__ volatile("push.w {r4-r9, lr}\nsub sp, #36\nmov r5, r1\nldr pc, =0x60029eed\n");
}
void mx1_sends_load(unsigned immediate,unsigned algorithm) {
    unsigned slot=SLOT;
    coefficient(slot?0x99:0x9a,0);
    barrier();
    ((void (*)(unsigned,unsigned))original_load)(immediate,algorithm);
    /* Internal return is enabled by flush only after its independent settings
     * have replaced the original loader's MASTER parameter replay. */
    if (!slot) { barrier(); coefficient(0x9a,ONE); }
}
static void effect_parameter(unsigned id,unsigned value) {
    /* Original registration records: ID, callback, secondary. Do not modify
     * the MASTER parameter store to configure the independent instance. */
    const u32 *record=(const u32 *)0x600b5594u;
    for (;record<(const u32 *)0x600b710cu;record+=3)
        if (record[0]==id) { FN(record[1],void (*)(u32,u32))(0,value); return; }
}
static void effect(unsigned cfg) {
    unsigned type=(cfg>>2)&7, algorithm=type<4?1:type==4?3:4;
    unsigned reload=!S.valid || ((S.applied>>2)&7)!=type || ALGO1!=algorithm;
    SLOT=1;
    if (reload) {
        mx1_sends_load(0,algorithm);
        const u32 *preset=(const u32 *)(0x60060ab0u+type*652u);
        unsigned first=algorithm==1?0x3d6:algorithm==3?0x3ec:0x3f4;
        unsigned last=algorithm==1?0x3dd:algorithm==3?0x3f3:0x3fa;
        for (unsigned id=first;id<=last;++id) effect_parameter(id,preset[id-0x3d3]);
    }
    if (reload || ((S.applied^cfg)&(127u<<5)))
        effect_parameter(algorithm==1?0x3da:algorithm==3?0x3ed:0x3f9,(cfg>>5)&127);
    if (reload || ((S.applied^cfg)&(127u<<12))) {
        unsigned time=(cfg>>12)&127;
        if (algorithm==1) {
            effect_parameter(0x3d8,0); /* Independent free time, no MASTER tempo sync. */
            effect_parameter(0x3d7,10000u+time*47000u); /* 10..5979 ms. */
        } else if (algorithm==3) {
            effect_parameter(0x3ef,time); effect_parameter(0x3f2,time);
        } else effect_parameter(0x3f5,time);
    }
    FN(0x6002a39du,void (*)(u32,u32))(0,0); /* No dry feedthrough. */
    FN(0x6002a9dbu,void (*)(u32,u32))(0,1); /* Always enabled, including tails. */
    SLOT=0;
    barrier();
    coefficient(0x99,ONE);
    S.applied=cfg; S.valid=1;
}
void mx1_sends_flush(void) {
    if (*(volatile u32 *)0x6051deb8u>3) { S.valid=0; return; }
    u32 cfg=config();
    unsigned external=parameter(0x19)==2;
    unsigned mode=external?0:cfg&3;
    const u32 *curve=(const u32 *)0x60077af4u;
    for (unsigned ch=0;ch<11;++ch) {
        coefficient(0x80+ch,external?0:curve[S.alt[ch]]);
        coefficient(0x8b+ch,external?0:curve[S.fx[ch]]);
    }
    coefficient(0x96,parameter(6)?ONE:0);
    coefficient(0x97,mode==1?ONE:0);
    coefficient(0x98,mode==2?ONE:0);
    if (mode==2 || S.phones)
        FN(0x60027ccfu,void (*)(u32,u32))(0,mode==2?0:
            FN(0x6001a1cfu,u32 (*)(u32,u32,u32))(0x60514504,0x20,0));
    S.phones=mode==2;
    if (external) { coefficient(0x99,0); return; }
    effect(cfg);
    coefficient(0x9a,ONE);
}
