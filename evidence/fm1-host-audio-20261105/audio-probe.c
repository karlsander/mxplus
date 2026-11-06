#include <CoreAudio/CoreAudio.h>
#include <CoreMIDI/CoreMIDI.h>
#include <CoreFoundation/CoreFoundation.h>
#include <mach/mach_time.h>
#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
static AudioStreamBasicDescription fmt;
static uint64_t frames, callbacks, firstHost,lastHost; static double firstSample,lastSample,peak,sumsq; static uint64_t nsamples;
static OSStatus prop(AudioObjectID o, AudioObjectPropertySelector sel, AudioObjectPropertyScope scope, UInt32 *sz, void *p) { AudioObjectPropertyAddress a={sel,scope,kAudioObjectPropertyElementMain}; return AudioObjectGetPropertyData(o,&a,0,NULL,sz,p); }
static OSStatus io(AudioDeviceID d,const AudioTimeStamp*now,const AudioBufferList*in,const AudioTimeStamp*t,AudioBufferList*out,const AudioTimeStamp*ot,void*c) {
    (void)d;(void)now;(void)out;(void)ot;(void)c;
    if(!callbacks) { firstHost=t->mHostTime; firstSample=t->mSampleTime; }
    lastHost=t->mHostTime;lastSample=t->mSampleTime;callbacks++;
    if(in->mNumberBuffers && fmt.mBytesPerFrame) frames+=in->mBuffers[0].mDataByteSize/fmt.mBytesPerFrame;
    if(fmt.mFormatID==kAudioFormatLinearPCM && (fmt.mFormatFlags&kAudioFormatFlagIsFloat) && fmt.mBitsPerChannel==32) {
        for(unsigned j=0;j<in->mNumberBuffers;j++) {float*p=in->mBuffers[j].mData; for(unsigned i=0;p&&i<in->mBuffers[j].mDataByteSize/4;i++){double x=p[i];if(fabs(x)>peak)peak=fabs(x);sumsq+=x*x;nsamples++;}}
    }
    return 0;
}
int main(void) {
    AudioObjectPropertyAddress a={kAudioHardwarePropertyDevices,kAudioObjectPropertyScopeGlobal,kAudioObjectPropertyElementMain}; UInt32 sz=0;AudioObjectGetPropertyDataSize(kAudioObjectSystemObject,&a,0,NULL,&sz);AudioDeviceID *ids=malloc(sz);AudioObjectGetPropertyData(kAudioObjectSystemObject,&a,0,NULL,&sz,ids);AudioDeviceID dev=0;
    for(unsigned i=0;i<sz/sizeof(*ids);i++){CFStringRef s=NULL;UInt32 n=sizeof(s);if(prop(ids[i],kAudioObjectPropertyName,kAudioObjectPropertyScopeGlobal,&n,&s))continue;char name[256];CFStringGetCString(s,name,sizeof(name),kCFStringEncodingUTF8);CFRelease(s);if(!strcmp(name,"FM1 Instrument")){dev=ids[i];break;}} free(ids);if(!dev)return 2;
    UInt32 n=sizeof(fmt);OSStatus e=prop(dev,kAudioDevicePropertyStreamFormat,kAudioObjectPropertyScopeInput,&n,&fmt);if(e)return 3;
    printf("{\n\"device\":\"FM1 Instrument\",\n\"logical_rate\":%.6f,\n\"logical_channels\":%u,\n\"logical_bits\":%u,\n\"logical_flags\":%u,\n",fmt.mSampleRate,fmt.mChannelsPerFrame,fmt.mBitsPerChannel,fmt.mFormatFlags);
    AudioStreamID streams[16];n=sizeof(streams);e=prop(dev,kAudioDevicePropertyStreams,kAudioObjectPropertyScopeInput,&n,streams);if(e||n<sizeof(*streams))return 4;
    AudioStreamBasicDescription physical; UInt32 q=sizeof(physical); e=prop(streams[0],kAudioStreamPropertyPhysicalFormat,kAudioObjectPropertyScopeGlobal,&q,&physical);printf("\"physical_format_status\":%d,\n\"physical_rate\":%.6f,\n\"physical_channels\":%u,\n\"physical_bits\":%u,\n",e,physical.mSampleRate,physical.mChannelsPerFrame,physical.mBitsPerChannel);
    AudioDeviceIOProcID proc=NULL;e=AudioDeviceCreateIOProcID(dev,io,NULL,&proc);printf("\"create_status\":%d,\n",e);if(e)return 5;
    e=AudioDeviceStart(dev,proc);printf("\"start_status\":%d,\n",e);fflush(stdout);if(!e){
    MIDIClientRef client=0;MIDIPortRef port=0;MIDIEndpointRef dest=0;
    fprintf(stderr,"client %d\n",MIDIClientCreate(CFSTR("MXPlus FM1 bench probe"),NULL,NULL,&client)); fprintf(stderr,"port %d\n",MIDIOutputPortCreate(client,CFSTR("FM1 test notes"),&port)); CFRunLoopRunInMode(kCFRunLoopDefaultMode,1,false);
    for(ItemCount i=0;i<MIDIGetNumberOfDestinations();i++){CFStringRef s=NULL;MIDIEndpointRef v=MIDIGetDestination(i);MIDIObjectGetStringProperty(v,kMIDIPropertyDisplayName,&s);char name[256]={0};if(s){CFStringGetCString(s,name,sizeof(name),kCFStringEncodingUTF8);CFRelease(s);}fprintf(stderr,"destination %s\n",name);if(strstr(name,"FM1") || !strcmp(name,"Felucca")){dest=v;break;}}
    printf("\"midi_destination_found\":%s,\n",dest?"true":"false");fflush(stdout);
    for(int i=0;i<20;i++){if(dest && i<8){MIDIPacketList l;MIDIPacket*p=MIDIPacketListInit(&l);Byte b[3]={i%2?0x80:0x90,(Byte)(60+2*(i/2)),i%2?0:48};MIDIPacketListAdd(&l,sizeof l,p,0,3,b);MIDISend(port,dest,&l);}usleep(500000);}
    if(port)MIDIPortDispose(port);if(client)MIDIClientDispose(client);AudioDeviceStop(dev,proc);
    }AudioDeviceDestroyIOProcID(dev,proc);
    mach_timebase_info_data_t tb;mach_timebase_info(&tb);double sec=(lastHost-firstHost)*(double)tb.numer/tb.denom/1e9;
    printf("\"callbacks\":%llu,\n\"frames\":%llu,\n\"timestamp_seconds\":%.9f,\n\"timestamp_sample_rate\":%.6f,\n\"peak\":%.9f,\n\"rms\":%.9f\n}\n",callbacks,frames,sec,sec?(lastSample-firstSample)/sec:0,peak,nsamples?sqrt(sumsq/nsamples):0);return e?6:0;
}
