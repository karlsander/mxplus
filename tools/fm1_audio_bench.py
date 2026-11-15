#!/usr/bin/env python3
"""Authorized B9 hardware bench over the existing FM-1 Bluetooth bridge.

Never called by reproduce.py. Requires the FM-1 bridge repository's client
and Python environment. Raw logs include local Bluetooth identifiers; keep
them private. Default is a short silent transport probe. --extended enables
the separate quiet-tone/converter sequence, with mute in cleanup.
"""
import argparse
import asyncio
import hashlib
import importlib.metadata
import json
from pathlib import Path
import platform
import sys
import time


async def run(args):
    sys.path.insert(0,str(args.bridge_tools.resolve()))
    from bridge import Bridge
    args.output.mkdir(parents=True,exist_ok=False)
    report={'candidate_file_sha256':hashlib.sha256(args.candidate.read_bytes()).hexdigest(),
            'macos':platform.mac_ver()[0],'python':platform.python_version(),
            'bleak':importlib.metadata.version('bleak'),'steps':[],'windows':[],
            'mx_frames':[],'cleanup':[]}
    ready=asyncio.Event()

    class Capture(Bridge):
        def record(self,kind,**data):
            super().record(kind,**data)
            if kind=='reply' and data.get('target')==1:
                report['mx_frames'].append({'time':time.time(),**data})
                if data.get('op') in (65,126) and len(data.get('words',[]))>1 and data['words'][1]==185:
                    ready.set()

    with (args.output/'raw.jsonl').open('x') as log:
        async with Capture(log=log) as b:
            print('Bluetooth capture connected; waiting for MX-1 B9.' if args.wait_boot else
                  'Bluetooth capture connected; checking MX-1 B9.',flush=True)
            engaged=False
            try:
                if args.wait_boot:
                    until=time.monotonic()+args.wait_boot
                    while not ready.is_set():
                        if time.monotonic()>=until:raise TimeoutError('No B9 heartbeat before boot wait expired')
                        report['last_waiting_fm']=await b.status()
                        await asyncio.sleep(2)
                report['before_mx']=await b.status(1)
                report['before_fm']=await b.status()
                if report['before_mx']['build']!=185 or report['before_fm']['build']!=177:
                    raise RuntimeError('This sequence requires MX B9 and FM bridge B1')
                if report['before_mx']['claimed'] or report['before_mx']['probe_pending']:
                    raise RuntimeError('Existing MX stream/probe: inspect it before starting another')
                engaged=True

                async def probe(step):
                    item={'step':step,'sent_at':time.time()};report['steps'].append(item)
                    item['accepted']=await b.command(5,[step],target=1)
                    item['ack_at']=time.time()
                    for _ in range(20):
                        await asyncio.sleep(.2);s=await b.status(1)
                        if s['probe_pending']==0 and s['probe_done']==step:break
                    else:raise TimeoutError(f'Manager step {step} did not finish')
                    item['mx']=s;item['fm']=await b.status()
                    print(json.dumps(item),flush=True)
                    if s['probe_result']:raise RuntimeError(f'Manager step {step} failed: {s["probe_result"]}')
                    return s

                async def pages():
                    rows={}
                    for page in (3,4,5,6,7,8,9,10,11,12,13,14):
                        try:rows[str(page)]=await b.command(2,[page],target=1)
                        except Exception as e:rows[str(page)]={'error':repr(e)}
                    return rows

                await b.command(3,[0])
                for step in (1,2,3):await probe(step)
                if not args.extended:
                    report['short_transports']=[]
                    modes=(args.short_probe,8 if args.short_probe==9 else 9) if args.compare_ioc else (args.short_probe,)
                    for index,step in enumerate(modes):
                        if index:
                            await probe(6);await probe(4)
                            for setup in (1,2,3):await probe(setup)
                        item={'probe':step,'before_fm':await b.status(),'before_mx':await b.status(1),'samples':[]}
                        report['short_transports'].append(item)
                        s=await probe(step)
                        for _ in range(20):
                            item['samples'].append({'time':time.time(),'mx':s,'fm':await b.status()})
                            if s['phase']==0 and not s['claimed']:break
                            await asyncio.sleep(.2);s=await b.status(1)
                        else:raise TimeoutError('Short transport did not retire')
                        item['after_mx']=s;item['after_fm']=await b.status();item['pages']=await pages()
                    report['completed_short_transport']=True
                    return
                await probe(7)
                for _ in range(12):
                    s=await b.status(1)
                    if s['phase']==2:break
                    if not s['claimed']:break
                    await asyncio.sleep(.25)
                report['start_status']=s;report['start_pages']=await pages()
                if s['phase']!=2:raise RuntimeError(f'Transport did not start: {s}')

                async def window(label,tone,mode,seconds):
                    await b.command(3,[tone]);await b.command(3,[mode],target=1)
                    item={'label':label,'fm_tone':tone,'mx_mode':mode,'samples':[]}
                    report['windows'].append(item)
                    print(f'{label}: {seconds} seconds',flush=True)
                    end=time.monotonic()+seconds
                    try:
                        while time.monotonic()<end:
                            sample={'time':time.time(),'fm':await b.status(),'mx':await b.status(1)}
                            item['samples'].append(sample);print(json.dumps(sample),flush=True)
                            if sample['mx']['phase']!=2 or not sample['mx']['wanted']:
                                raise RuntimeError('Transport stopped during observation')
                            await asyncio.sleep(.5)
                    finally:
                        item['pages']=await pages()

                await window('USB silence, converter bypassed',0,3,2)
                await window('FM-1 stereo packets, converter bypassed',1,3,6)
                await window('FM-1 stereo USB tone through converter, 220/440 Hz',1,0,4)
                await window('MX-1 local converter tone, 220 Hz',0,2,4)
                report['completed_windows']=True
            except Exception as e:
                report['error']=repr(e);print('Bench stopped: '+repr(e),flush=True)
            finally:
                if engaged:
                    # Mute the device even when the MX command direction failed.
                    for target,op,words,label in [(0,3,[0],'FM mute'),(1,5,[6],'MX stop')]:
                        try:report['cleanup'].append({label:await b.command(op,words,target=target)})
                        except Exception as e:report['cleanup'].append({label+'_error':repr(e)})
                    # FM Bluetooth remains useful when the MX MIDI path fails.
                    # Keep its status/trace independent of every MX readout.
                    try:
                        for _ in range(20):
                            s=await b.status(1)
                            if not s['probe_pending'] and not s['claimed'] and s['phase']==0:break
                            await asyncio.sleep(.25)
                        if not s['probe_pending'] and not s['claimed'] and s['phase']==0:
                            report['cleanup'].append({'alt0_accepted':await b.command(5,[4],target=1)})
                            await asyncio.sleep(.5)
                        report['after_mx']=await b.status(1)
                    except Exception as e:report['cleanup'].append({'mx_readout_error':repr(e)})
                    # Read FM after the alt0 operation, so this really is final state.
                    try:report['after_fm']=await b.status()
                    except Exception as e:report['cleanup'].append({'fm_readout_error':repr(e)})
                    try:
                        report['after_midi']=await b.command(2,[4],target=1)
                    except Exception as e:report['cleanup'].append({'midi_readout_error':repr(e)})
                    report['after_pages']=await pages()
                    try:
                        report['trace']=[];cursor=report.get('before_fm',{}).get('trace_total',0)
                        for _ in range(16):
                            page=await b.command(2,[cursor]);report['trace'].append(page)
                            if len(page)>3:cursor=page[-5]+1
                            if cursor>=page[1]:break
                    except Exception as e:report['cleanup'].append({'trace_readout_error':repr(e)})
                (args.output/'result.json').write_text(json.dumps(report,indent=2)+'\n')
                print(json.dumps({'output':str(args.output),'error':report.get('error'),
                                  'after_fm':report.get('after_fm'),'after_mx':report.get('after_mx')}),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--bridge-tools',type=Path,required=True)
    p.add_argument('--candidate',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    p.add_argument('--wait-boot',type=int,default=0,help='Seconds to wait for B9 heartbeat before sending MX commands')
    p.add_argument('--short-probe',type=int,choices=(8,9),default=9,help='9: poll-only; 8: prior IOC policy')
    p.add_argument('--compare-ioc',action='store_true',help='Run both short policies, stopping and selecting alt0 between them')
    p.add_argument('--extended',action='store_true',help='Run the longer tone/converter sequence instead of the default silent two-second probe')
    args=p.parse_args()
    if args.extended and args.compare_ioc:p.error('--compare-ioc requires the short sequence')
    if not (args.bridge_tools/'bridge.py').is_file() or args.candidate.stat().st_size!=4194320:
        p.error('Expected the existing FM-1 bridge tools and a full MX-1 candidate')
    asyncio.run(run(args))
