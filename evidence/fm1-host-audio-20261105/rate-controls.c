#include <libusb.h>
#include <stdio.h>
int main(void){libusb_context*c=0;if(libusb_init(&c))return 1;libusb_device_handle*h=libusb_open_device_with_vid_pid(c,0x1209,1);if(!h)return 2;unsigned char b[3]={0};int r=libusb_control_transfer(h,0xa2,0x81,0x100,0x84,b,3,1000);printf("{\"get_cur_result\":%d,\"get_cur_hex\":\"%02x%02x%02x\",",r,b[0],b[1],b[2]);b[0]=0x44;b[1]=0xac;b[2]=0;r=libusb_control_transfer(h,0x22,1,0x100,0x84,b,3,1000);printf("\"set_cur_44100_result\":%d}\n",r);libusb_close(h);libusb_exit(c);return 0;}
