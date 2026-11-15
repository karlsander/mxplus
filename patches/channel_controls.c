/* Channel-owned tempo surface; independently written 2026-11-15.
 * Empty pages only: no parameter, audio, storage or clock changes. */
#pragma clang section text=".channel_head" rodata=".channel_rodata" bss=".channel_state"
typedef unsigned char u8;
typedef unsigned short u16;
#define FN(a,t) ((t)(a))
#define MIX ((void *)0x600b53acu)
#define DIRTY (*(volatile u16 *)0x605141ccu)
#define KEYS ((volatile u8 *)0x605129a4u)
extern int mx1_master_is_active(void);
struct channel_state { u8 page[11], swallowed, shown; };
struct channel_state mx1_channel_state;
#define S mx1_channel_state
/* Stock current-channel and selected flags are authoritative, including linked
 * and multiple selection. No parallel selection state is introduced. */
int mx1_channel_selected(void) {
    unsigned page=*(volatile u16 *)0x600b4b5eu;
    if (*(volatile unsigned *)0x600b4b94u || *(volatile unsigned *)0x600b537cu ||
        !((page>=5 && page<=10) || page==15) || mx1_master_is_active() ||
        FN(0x60018259u,int (*)(void *))((void *)0x605144ccu)) return -1;
    int strip=FN(0x6001e65fu,int (*)(void *,unsigned,unsigned))(MIX,0xfb,0);
    if ((unsigned)strip>=11 ||
        !FN(0x6001e65fu,int (*)(void *,unsigned,unsigned))(MIX,(unsigned)strip,0)) return -1;
    return strip;
}
/* Called before the original full redraw, including MIDI/scene selection
 * changes. Selection dirties the right display and tempo LEDs as well. */
void mx1_channel_refresh(void) {
    unsigned shown=(unsigned)(mx1_channel_selected()+1);
    if (shown!=S.shown) { S.shown=(u8)shown; DIRTY|=0x500; }
}
void mx1_channel_display(unsigned strip) {
    char label[4]={'P',(char)('1'+S.page[strip]),'-','-'};
    FN(0x60054f85u,void (*)(void *,unsigned,const char *,unsigned))
        ((void *)0x60512984u,1,label,0);
}
/* Replace the original mono LED helper, preserving its five-argument text
 * driver call. This also intercepts asynchronous TAP beat-light updates. */
void mx1_channel_led(unsigned id,unsigned mode,unsigned brightness) {
    if (id>=10 && id<=13) {
        int strip=mx1_channel_selected();
        if (strip>=0) mode=(id-10==S.page[strip]);
    }
    FN(0x01002ad3u,void (*)(void *,unsigned,unsigned,unsigned,unsigned))
        ((void *)0x60512984u,id,mode,brightness,0);
}
int mx1_channel_keys_held(void) { return S.swallowed!=0; }
#pragma clang section text=".channel_text"
static unsigned button_page(unsigned id) {
    if (id==0) return 3;
    return id>=0x1b && id<=0x1d?id-0x1b:4;
}
/* Runs before mastering dispatch, so release ownership survives entry/exit.
 * Duplicate down packets must not become fresh tempo presses after deselect. */
int mx1_channel_owned_event(const u8 *event) {
    unsigned type=event[0],page=button_page(event[1]);
    if (type<1 || type>3 || page>=4) return 0;
    unsigned bit=1u<<page;
    if (!(S.swallowed&bit)) return 0;
    if (type==1) { S.swallowed&=(u8)~bit; DIRTY|=0x500; }
    return 1;
}
/* Return nonzero only for owned controls. Stock-held releases are delivered
 * for cleanup; channel-held releases/repeats stay consumed across selection,
 * menu and mode transitions. SELECT + TEMPO routing is handled first. */
int mx1_channel_event(const u8 *event) {
    unsigned type=event[0],id=event[1];
    if (type==4 && id==1) return mx1_channel_selected()>=0;
    if (type<1 || type>3) return 0;
    unsigned page=button_page(id);
    if (page>=4) return 0;
    int strip=mx1_channel_selected();
    if (type==2 && strip>=0) {
        /* A duplicate stock-held press must not steal its eventual release. */
        if (KEYS[id/8]&(1u<<(id&7))) return 1;
        S.swallowed|=(u8)(1u<<page); S.page[strip]=(u8)page;
        DIRTY|=0x500; mx1_channel_display((unsigned)strip); return 1;
    }
    /* A key pressed in stock mode must get its release, even after selection.
     * Other orphan repeats/releases cannot enter tempo actions. */
    return strip>=0 && !(KEYS[id/8]&(1u<<(id&7)));
}
