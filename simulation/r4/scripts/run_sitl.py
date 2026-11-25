"""Run actual ArduCopter + native Simulink physics on localhost only.
No serial devices or real flight controllers are accessed.
"""
from pathlib import Path
import sys,os,time,json,subprocess,socket,hashlib,argparse
ROOT=Path(__file__).resolve().parent.parent
os.environ['MAVLINK20']='1'
from pymavlink import mavutil
MATLAB=Path(os.environ.get('MATLAB_EXE', r'C:\Program Files\MATLAB\R2025b\bin\matlab.exe'))
EXE=ROOT/'runtime/ardupilot/arducopter.exe'
FLAGS=subprocess.CREATE_NO_WINDOW if os.name=='nt' else 0

def run_case(name,instance=0,output_name=None):
    definition=next(c for c in json.loads((ROOT/'config/cases.json').read_text()) if c['name']==name)
    variant=definition['profile']
    assert instance==0,'This package uses one simulator instance.'
    runtime=ROOT
    out=ROOT/'results'/(output_name or name)
    if out.exists() and any(out.iterdir()):
        raise FileExistsError(f'Preserving existing recording: {out}. Choose a fresh output_name or archive an invalid attempt first.')
    out.mkdir(parents=True,exist_ok=True)
    base=ROOT/'config'/f'{variant}.parm'
    ap_args=[str(EXE),'--instance',str(instance),'--sysid','1','-S','--model','JSON:127.0.0.1','--speedup','5','--rate','1200','--wipe',
      '--home','-35.363261,149.165230,584,0','--defaults',(ROOT/'config/copter.parm').as_posix()+','+base.as_posix()]
    metadata={'case':name,'variant':variant,'firmware_sha256':hashlib.sha256(EXE.read_bytes()).hexdigest(),
      'firmware_source_commit':'bf693f316b0144fb4fac3893956f80f4c277fa3f','argv':ap_args,
      'simulation_only':True,'real_devices_accessed':False,'instance':instance,'json_port':9002+10*instance,'mavlink_port':5760+10*instance,'controller_sha256':hashlib.sha256(base.read_bytes()).hexdigest()}
    (out/'run_metadata.json').write_text(json.dumps(metadata,indent=2))
    ap_log=(out/'ardupilot_console.log').open('wb')
    ap=subprocess.Popen(ap_args,cwd=out,stdout=ap_log,stderr=subprocess.STDOUT,creationflags=FLAGS)
    mat=None;m=None;telemetry=None;flow_socket=None;flow_log=None;flow_count=0
    try:
        if variant.startswith('flow'):
            flow_socket=socket.socket(socket.AF_INET,socket.SOCK_DGRAM);flow_socket.bind(('127.0.0.1',9450+10*instance));flow_socket.setblocking(False)
            flow_log=(out/'flow_mavlink_sent.jsonl').open('w')
        # Make one real MAVLink connection. A connect/disconnect port probe
        # would consume the simulator's first TCP session during initialization.
        deadline=time.monotonic()+90
        while True:
            if ap.poll() is not None:raise RuntimeError(f'ArduPilot exited {ap.returncode}')
            try:
                m=mavutil.mavlink_connection(f'tcp:127.0.0.1:{5760+10*instance}',source_system=255,autoreconnect=True,retries=1);break
            except OSError:
                if time.monotonic()>deadline:raise TimeoutError('No local ArduPilot MAVLink port')
                time.sleep(.2)
        script=f"cd('{(runtime/'model').as_posix()}'); run_ap_case('{name}','{out.as_posix()}')"
        mat=subprocess.Popen([str(MATLAB),'-batch',script,'-logfile',str(out/'matlab.log')],cwd=runtime/'model',
          stdout=subprocess.DEVNULL,stderr=subprocess.STDOUT,creationflags=FLAGS)
        telemetry=(out/'telemetry.jsonl').open('w')
        latest_t=0.;armed=False;actual_mode=-1;arm_time=None;requested=False;param_values={};commands=[];param_queue=[];firmware_version=None
        last_param=-100.;seen_status=set();last_stream_request=-100.;timed_message_seen=False;last_origin=-100.;origin_seen=False;first_native_clock=None
        last_native_status=-100.;land_request_time=None;land_mode_time=None;native_disarm_time=None;last_land_command=-100.;status_write_retries=0
        last_rc=-100.;last_heartbeat=-100.;last_arm=-100.;last_mode=-100.;wall_start=time.monotonic();last_progress=-100.
        while mat.poll() is None:
            wall=time.monotonic()
            if wall-wall_start>3600:raise TimeoutError('Simulation exceeded 60 minute wall-time limit')
            if flow_socket is not None:
                for _ in range(200):
                    try:raw,_address=flow_socket.recvfrom(65535)
                    except BlockingIOError:break
                    packet=json.loads(raw)
                    m.mav.optical_flow_send(int(packet['sampleTime']*1e6),0,0,0,0.,0.,int(packet['quality']),-1.,flow_rate_x=float(packet['flowX']),flow_rate_y=float(packet['flowY']))
                    flow_log.write(json.dumps({**packet,'native_clock_at_send_s':latest_t})+'\n');flow_count+=1
            msg=m.recv_match(blocking=False)
            if msg:
                d=msg.to_dict();d['host_elapsed_s']=wall-wall_start
                telemetry.write(json.dumps(d,default=lambda v:list(v) if isinstance(v,(bytes,bytearray)) else str(v))+'\n')
                typ=msg.get_type()
                if typ=='AUTOPILOT_VERSION':firmware_version=d
                if typ=='GPS_GLOBAL_ORIGIN':origin_seen=True
                if 'time_boot_ms' in d:
                    latest_t=max(latest_t,float(d['time_boot_ms'])/1000);timed_message_seen=True
                # Native TIMESYNC originates from the same SITL boot clock.
                # It bootstraps supervision when initial stream requests arrive
                # during firmware initialization and are not yet accepted.
                if typ=='TIMESYNC' and d.get('tc1')==0:
                    if first_native_clock is None:first_native_clock=float(d['ts1'])/1e9
                    latest_t=max(latest_t,float(d['ts1'])/1e9)
                if typ=='STATUSTEXT' and d.get('text','') not in seen_status:
                    seen_status.add(d.get('text',''));print(f'[{name}] {d.get("text","")}',flush=True)
                if typ=='PARAM_VALUE':param_values[str(msg.param_id)]=float(msg.param_value)
                if typ=='HEARTBEAT' and msg.get_srcSystem()==1:
                    actual_mode=msg.custom_mode
                    if land_request_time is not None and actual_mode==9 and land_mode_time is None:land_mode_time=latest_t
                    armed=bool(msg.base_mode & mavutil.mavlink.MAV_MODE_FLAG_SAFETY_ARMED)
                    if armed and arm_time is None:arm_time=latest_t;print(f'[{name}] ARMED at {arm_time:.2f}s',flush=True)
                    if arm_time is not None and not armed and native_disarm_time is None:native_disarm_time=latest_t;print(f'[{name}] NATIVE DISARM at {latest_t:.2f}s',flush=True)
                    if not requested:
                        requested=True
                        m.mav.command_long_send(1,1,mavutil.mavlink.MAV_CMD_REQUEST_MESSAGE,0,148,0,0,0,0,0,0)
                        for mid,hz in [(30,40),(32,20),(2,10),(36,20),(173,20),(83,20),(193,5),(49,1),(230,10),(106,20),(24,10)]:
                            m.mav.command_long_send(1,1,mavutil.mavlink.MAV_CMD_SET_MESSAGE_INTERVAL,0,mid,1e6/hz,0,0,0,0,0)
                        param_queue=['FRAME_CLASS','AHRS_EKF_TYPE','EK3_SRC1_POSZ','GPS1_TYPE','RNGFND1_TYPE',
                           'RNGFND1_MIN','RNGFND1_MAX','PILOT_TKO_ALT_M','PILOT_SPD_UP','PILOT_ACC_Z',
                           'PSC_D_POS_P','PSC_D_VEL_P','PSC_D_ACC_P','ATC_RAT_RLL_P','ATC_RAT_PIT_P',
                           'ATC_RAT_YAW_P','SERVO1_FUNCTION','SERVO2_FUNCTION','SERVO3_FUNCTION','SERVO4_FUNCTION',
                           'SERVO5_FUNCTION','MOT_THST_HOVER','MOT_THST_EXPO','SERVO1_TRIM','SERVO2_TRIM',
                           'SERVO3_TRIM','SERVO4_TRIM','AHRS_TRIM_X','AHRS_TRIM_Y','TKOFF_SLEW_TIME','TKOFF_THR_MAX',
                           'EK3_SRC1_POSXY','EK3_SRC1_VELXY','INS_ACCOFFS_X','INS_ACCOFFS_Y','INS_ACCSCAL_X','INS_ACCSCAL_Y','SIM_DRIFT_SPEED','SCHED_LOOP_RATE','ARMING_SKIPCHK','EK3_IMU_MASK','INS_USE2','INS_USE3','SIM_RATE_HZ','FLOW_TYPE','SIM_FLOW_ENABLE','SIM_FLOW_RATE','SIM_FLOW_RND','SIM_FLOW_DELAY','SIM_FLOW_POS_Z','FLOW_POS_Z','EK3_FLOW_DELAY','EK3_FLOW_M_NSE','EK3_FLOW_USE','PSC_NE_POS_P','PSC_NE_VEL_P','PSC_NE_VEL_I','PSC_NE_VEL_D','LOIT_SPEED_MS','LOIT_ACC_MAX_M','LOIT_ANG_MAX','SIM_GPS1_HZ','SIM_GPS1_LAG_MS','SIM_GPS1_ACC','FLOW_FXSCALER','FLOW_FYSCALER','LAND_SPD_HIGH_MS','LAND_SPD_MS','LAND_ALT_LOW_M','LAND_REPOSITION','DISARM_DELAY']
                if typ=='COMMAND_ACK':commands.append(d)
                continue
            if wall-last_native_status>=.05:
                status={'native_time_s':latest_t,'armed':armed,'had_armed':arm_time is not None,'mode':actual_mode,'native_disarm_s':native_disarm_time}
                temp=out/'native_status.tmp';temp.write_text(json.dumps(status))
                try:temp.replace(out/'native_status.json')
                except PermissionError:status_write_retries+=1
                last_native_status=wall
                phase_path=out/'mission_status.json'
                if phase_path.exists():
                    try:phase=json.loads(phase_path.read_text())
                    except (OSError,json.JSONDecodeError):phase={}
                    if phase.get('land_requested') and land_request_time is None:
                        land_request_time=latest_t;print(f'[{name}] REQUEST LAND after full hover at {latest_t:.2f}s',flush=True)
            if land_request_time is not None and land_mode_time is None and wall-last_land_command>1:
                m.set_mode(9);last_land_command=wall
            if wall-last_heartbeat>=1:
                m.mav.heartbeat_send(mavutil.mavlink.MAV_TYPE_GCS,mavutil.mavlink.MAV_AUTOPILOT_INVALID,0,0,0)
                last_heartbeat=wall
            if requested and not timed_message_seen and wall-last_stream_request>=5:
                for mid,hz in [(30,40),(32,20),(2,10),(36,20),(173,20),(83,20),(193,5),(49,1),(230,10),(106,20),(24,10)]:
                    m.mav.command_long_send(1,1,mavutil.mavlink.MAV_CMD_SET_MESSAGE_INTERVAL,0,mid,1e6/hz,0,0,0,0,0)
                last_stream_request=wall
            if first_native_clock is not None and latest_t-first_native_clock>40 and not timed_message_seen:
                raise RuntimeError('Timed telemetry stream did not initialize; invalid ground-only attempt')
            if param_queue and latest_t-last_param>=.2:
                m.mav.param_request_read_send(1,1,param_queue.pop(0).encode(),-1);last_param=latest_t
            if latest_t>=25 and variant.startswith('flow') and not origin_seen and wall-last_origin>1:
                m.mav.set_gps_global_origin_send(1,-353632610,1491652300,584000);last_origin=wall
            if latest_t>=25 and actual_mode!=5 and arm_time is None and wall-last_mode>1:
                m.set_mode(5);last_mode=wall
            if latest_t>=30 and actual_mode==5 and not armed and wall-last_arm>2:
                m.mav.command_long_send(1,1,mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM,0,1,0,0,0,0,0,0)
                last_arm=wall
            if wall-last_rc>=.05:
                throttle=1000
                if arm_time is not None and land_request_time is None:
                    elapsed=latest_t-arm_time
                    throttle=1600 if 1<=elapsed<3 else (1500 if elapsed>=3 else 1000)
                m.mav.rc_channels_override_send(1,1,1500,1500,throttle,1500,1500,1500,1500,1500)
                last_rc=wall
            if wall-last_progress>15:
                print(f'[{name}] firmware t={latest_t:.1f}s, mode={actual_mode}, armed={armed}, MATLAB running',flush=True);last_progress=wall
                telemetry.flush()
            time.sleep(.001)
        if mat.returncode!=0:raise RuntimeError(f'MATLAB failed ({mat.returncode}); see {out/"matlab.log"}')
        metadata.update({'armed':arm_time is not None,'final_flight_mode':actual_mode,'arm_time_firmware_s':arm_time,'last_firmware_time_s':latest_t,
          'matlab_exit_code':mat.returncode,'parameters_read_back':param_values,'autopilot_version':firmware_version,'command_acks':commands,'ekf_origin_seen':origin_seen,'flow_mavlink_packets_sent':flow_count,'land_request_native_s':land_request_time,'land_mode_native_s':land_mode_time,'native_disarm_s':native_disarm_time,'status_file_retry_count':status_write_retries})
        (out/'run_metadata.json').write_text(json.dumps(metadata,indent=2))
        print(f'COMPLETED {variant}/{name}: armed={arm_time is not None}',flush=True)
    finally:
        if mat is not None and mat.poll() is None:
            if os.name=='nt':subprocess.run(['taskkill','/PID',str(mat.pid),'/T','/F'],stdout=subprocess.DEVNULL,stderr=subprocess.STDOUT,creationflags=FLAGS)
            else:mat.terminate()
            mat.wait(timeout=30)
        if m:m.close()
        if telemetry:telemetry.close()
        if flow_log:flow_log.close()
        if flow_socket:flow_socket.close()
        if ap.poll() is None:ap.terminate();ap.wait(timeout=30)
        ap_log.close()
    return out

