/* MX-1 USB-host enumeration experiment, independently written 2026-11-01.
 * This is a narrow research profile, NOT a general UAC1/UAC2 host driver.
 * Transport still uses Roland's original high-speed, 8-microframe engine.
 * See docs/HOST_PROBE.md and the machine-code tests before considering hardware.
 */
typedef unsigned char u8;
typedef unsigned short u16;
typedef unsigned int u32;
extern void mx1_original_classify(u8 *, const u8 *, const u8 *);
extern int mx1_original_configuration(u8 *, const u8 *);
void mx1_uac1_classify(u8 *, const u8 *, const u8 *);

static u32 rd16(const u8 *p) { return p[0] | ((u32)p[1] << 8); }
static u32 rd24(const u8 *p) { return rd16(p) | ((u32)p[2] << 16); }
static u32 rd32(const u8 *p) { return rd24(p) | ((u32)p[3] << 24); }
static int rate_ok(u32 r) { return r == 44100 || r == 48000 || r == 96000; }
static void clear_record(u8 *r) { for (u32 i=0;i<18;i++) r[i]=0; }

/* Classify one standard UAC1 alt1 with a single, fixed rate and one ISO data
 * endpoint. Endpoint timing and sample layout must match the existing engine.
 * The original parser's 18-byte output is preserved, including direction codes.
 */
static int active(u8 *out, const u8 *itf, const u8 *end) {
    const u8 *general=0, *format=0, *ep=0;
    if (itf >= end || (u32)(end-itf) < 9 || itf[0] != 9 || itf[1] != 4 ||
        itf[3] != 1 || itf[4] != 1 || itf[5] != 1 || itf[6] != 2 || itf[7] != 0)
        return 0;
    for (const u8 *p=itf+9;p<end;) {
        if ((u32)(end-p)<2 || p[0]<2 || p[0]>(u32)(end-p)) return 0;
        if (p[1]==4) break;
        if (p[1]==0x24) {
            if (p[0]<3) return 0;
            if (p[2]==1) { if (general) return 0; general=p; }
            if (p[2]==2) { if (format) return 0; format=p; }
        }
        if (p[1]==5) { if (ep) return 0; ep=p; }
        p+=p[0];
    }
    if (!general || general[0]<7 || rd16(general+5)!=1 ||
        !format || format[0]!=11 || format[3]!=1 || format[4]!=2 ||
        format[5]!=4 || format[6]!=24 || format[7]!=1 ||
        !ep || ep[0]<7 || !(ep[2]&15) || (ep[2]&0x70) ||
        !((ep[3]==5) || ((ep[2]&0x80) && ep[3]==0x25)) || ep[6]!=1 ||
        rd16(ep+4)==0 || rd16(ep+4)>1023 || (ep[0]>=9 && ep[8]!=0)) return 0;
    u32 rate=rd24(format+8);
    if (!rate_ok(rate)) return 0;
    /* Largest packet at the selected rate, plus one sample for clock variation. */
    u32 minimum=((rate+7999)/8000+1)*8;
    if (rd16(ep+4)<minimum) return 0;
    clear_record(out);
    out[0]=(ep[2]&0x80)?4:2;
    out[4]=(u8)rate;out[5]=(u8)(rate>>8);out[6]=(u8)(rate>>16);out[7]=0;
    out[8]=4;out[9]=1;out[10]=24;out[11]=2;
    out[12]=itf[2];out[13]=itf[3];
    return 1;
}

/* Retain origin information in the stock stream record's reserved byte. The
 * stock info builder copies it to info entry[7], while the audio engine ignores
 * it. Without this marker, an unrelated vendor-class descriptor could bypass
 * the strict UAC1 checks above and still match the summarized audio format.
 */
int mx1_uac1_configuration(u8 *state, const u8 *config) {
    if (!config || config[0]!=9 || config[1]!=2) return -1;
    u32 length=rd16(config+2);
    if (length<9 || length>4096) return -1;
    const u8 *end=config+length;
    for (const u8 *p=config;p<end;) {
        if ((u32)(end-p)<2 || p[0]<2 || p[0]>(u32)(end-p)) return -1;
        if (p[1]==4 && (p[0]<9 || p[2]>=8)) return -1;
        p+=p[0];
    }
    int result=mx1_original_configuration(state,config);
    if (result) return result;
    for (u32 alt=0;alt<5;alt++) {
        state[0x10+alt*0x14+0x0f]=0;
        state[0x74+alt*0x14+0x0f]=0;
    }
    for (const u8 *p=config;p<end;p+=p[0]) {
        if (p[1]==4) {
            u8 record[18];
            mx1_uac1_classify(record,p,end);
            if (record[0]>=1 && record[0]<=4 && record[13]<5) {
                u32 base=record[0]>=3?0x10:0x74;
                /* Follow the same descriptor order as the original parser:
                 * a later vendor record must clear an earlier generic marker.
                 * Mark alt0 as well: its classifier already requires the
                 * following valid alt1 to have the same interface number. */
                state[base+record[13]*0x14+0x0f]=p[5]==1?0xa5:0;
            }
        }
    }
    return 0;
}

__attribute__((section(".text.hook")))
void mx1_uac1_classify(u8 *out, const u8 *itf, const u8 *end) {
    /* Existing Roland parsing is delegated to untouched instructions after an
     * exact prologue trampoline. This keeps the supported-device behavior. */
    if (itf<end && (u32)(end-itf)>=9 && itf[5]==0xff) {
        mx1_original_classify(out,itf,end);
        return;
    }
    clear_record(out);
    if (itf>=end || (u32)(end-itf)<9 || itf[0]!=9 || itf[1]!=4 ||
        itf[5]!=1 || itf[6]!=2 || itf[7]!=0 || itf[3]>1) return;
    out[12]=itf[2];out[13]=itf[3];
    if (itf[3]==1) { active(out,itf,end); return; }
    if (itf[4]!=0) return;
    /* A standard alt0 carries no endpoint direction. Look at its matching alt1
     * rather than interpreting Roland's proprietary protocol byte as direction. */
    for (const u8 *p=itf+9;p<end;) {
        if ((u32)(end-p)<2 || p[0]<2 || p[0]>(u32)(end-p)) return;
        if (p[1]==4) {
            if (p[0]<9 || p[2]!=itf[2]) return;
            if (p[3]==1) {
                if (active(out,p,end)) {
                    out[0]-=1;out[13]=0;
                }
                return;
            }
        }
        p+=p[0];
    }
}

/* The main host selects equal alternate numbers for input and output. Only the
 * already-supported 4-byte stereo PCM profile is enabled for non-Roland VIDs.
 * No arbitrary vendor MIDI interface is admitted by this extension.
 */
__attribute__((section(".text.policy")))
void mx1_uac1_policy(const u8 *info, u8 *selection) {
    if (rd16(info)==0x0582) {
        ((void (*)(const u8*,u8*))0x60007bf9u)(info,selection);
        return;
    }
    clear_record(selection);
    if (rd32(info+8)!=1 || rd32(info+12)!=2 || rd32(info+0x38)!=2 ||
        info[0x17]!=0xa5 || info[0x43]!=0xa5) return;
    const u8 *a=info+0x18,*b=info+0x44;
    if (rd32(a)!=rd32(b) || !rate_ok(rd32(a)) ||
        a[4]!=4 || b[4]!=4 || a[5]!=1 || b[5]!=1 || a[6]!=2 || b[6]!=2 ||
        a[7]!=0xa5 || b[7]!=0xa5) return;
    selection[0]=1;selection[2]=1;
    selection[6]=1;selection[8]=1;
}
