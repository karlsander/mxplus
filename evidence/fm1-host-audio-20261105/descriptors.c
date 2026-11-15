#include <libusb.h>
#include <stdio.h>
int main(void) {
    libusb_context *ctx=0; if(libusb_init(&ctx)) return 1;
    libusb_device_handle *h=libusb_open_device_with_vid_pid(ctx,0x1209,1);
    if(!h) {fprintf(stderr,"FM1 open failed\n");return 2;}
    printf("{\n  \"libusb_speed\": %d",libusb_get_device_speed(libusb_get_device(h)));
    unsigned char b[4096];
    for(int type=1;type<=2;type++) {
        int n=libusb_control_transfer(h,0x80,6,type<<8,0,b,type==1?18:sizeof b,1000);
        printf(",\n  \"%s_result\": %d",type==1?"device":"configuration",n);
        if(n<0) continue;
        printf(",\n  \"%s_hex\": \"",type==1?"device":"configuration");
        for(int i=0;i<n;i++) printf("%02x",b[i]); printf("\"");
    }
    printf("\n}\n");libusb_close(h);libusb_exit(ctx);return 0;
}
