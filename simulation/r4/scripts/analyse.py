from pathlib import Path
import json,sys
ROOT=Path(__file__).resolve().parent.parent
import numpy as np
from pymavlink import mavutil
def analyse(name,recording_directory=None):
 f=Path(recording_directory) if recording_directory is not None else ROOT/'results'/name;meta=json.loads((f/'run_metadata.json').read_text());p=json.loads((f/'plant_parameters.json').read_text())
 assert meta['matlab_exit_code']==0
 d=np.genfromtxt(f/'physics.csv',delimiter=',',names=True);assert all(np.isfinite(d[k]).all() for k in d.dtype.names)
 t=d['Time_s'];assert (np.diff(t)>0).all();dt=float(np.median(np.diff(t)))
 mission=json.loads((f/'mission_status.json').read_text()) if (f/'mission_status.json').exists() else {}
 definition=next(c for c in json.loads((ROOT/'config/cases.json').read_text()) if c['name']==name)
 assert p['tetherEnabled']==0 and np.max(d['MaxLineTension_N'])==0
 assert abs(p['mass']-2.0128)<1e-9 and np.max(abs(np.array(p['windWorld'])-definition['windWorld']))<1e-12
 needed={'ARMING_SKIPCHK','AHRS_EKF_TYPE','GPS1_TYPE','EK3_SRC1_POSXY','EK3_SRC1_VELXY','EK3_SRC1_POSZ',
 'SCHED_LOOP_RATE','SIM_RATE_HZ','LAND_SPD_HIGH_MS','LAND_SPD_MS','LAND_ALT_LOW_M','LAND_REPOSITION','DISARM_DELAY',
 'ATC_ANG_RLL_P','ATC_ANG_PIT_P','ATC_RAT_RLL_P','ATC_RAT_RLL_I','ATC_RAT_RLL_D','ATC_RAT_PIT_P','ATC_RAT_PIT_I','ATC_RAT_PIT_D',
 'AHRS_TRIM_X','AHRS_TRIM_Y','SERVO1_TRIM','SERVO2_TRIM','SERVO3_TRIM','SERVO4_TRIM',
 'PSC_NE_POS_P','PSC_NE_VEL_P','PSC_NE_VEL_I','PSC_NE_VEL_D','SIM_GPS1_HZ','SIM_GPS1_LAG_MS','SIM_GPS1_ACC','SIM_GPS1_VERR_X','SIM_GPS1_VERR_Y'}
 actual={};records={'MODE':[],'ARM':[],'MSG':[],'GPS':[],'PSCN':[]}
 log=mavutil.mavlink_connection(str(next((f/'logs').glob('*.BIN'))))
 while True:
  msg=log.recv_match(type=['PARM',*records])
  if msg is None:break
  typ=msg.get_type()
  if typ=='PARM' and msg.Name in needed and msg.Name not in actual:actual[msg.Name]=msg.Value
  elif typ in records:records[typ].append(msg.to_dict())
 log.close()
 for key in needed-set(actual):
  if key in meta['parameters_read_back']:actual[key]=meta['parameters_read_back'][key]
 assert not needed-set(actual),('Missing native parameter evidence',needed-set(actual))
 expected={}
 for line in (ROOT/'config/gps_good.parm').read_text().splitlines():
  w=line.split()
  if w and not w[0].startswith('#'):expected[w[0]]=float(w[1])
 for key in needed:assert abs(actual[key]-expected[key])<1e-6,(key,actual[key],expected[key])
 (f/'verified_firmware_parameters.json').write_text(json.dumps(actual,indent=2))
 modes=[v['ModeNum'] for v in records['MODE']];assert 5 in modes
 first=modes.index(5);allowed=all(v in [5,9] for v in modes[first:]);entered_land=9 in modes
 if entered_land:allowed=allowed and all(v==9 for v in modes[modes.index(9):])
 n=max(1,round(.1/dt));lift=np.flatnonzero(np.convolve((d['FootClearance_m']>.003).astype(int),np.ones(n,dtype=int),'valid')>=n)
 liftoff=float(t[lift[0]]) if len(lift) else None
 hs=mission.get('hover_start_s',-1);ls=mission.get('land_request_sim_s',-1)
 hover_complete=bool(hs>=0 and ls>=hs+8-dt*1.1)
 hover=(t>=hs-1e-8)&(t<=hs+8+1e-8) if hover_complete else np.zeros(len(t),bool)
 radius=np.hypot(d['X_m'],d['Y_m']);lean=np.rad2deg(np.arccos(np.clip(np.cos(np.deg2rad(d['CAD_RollX_deg']))*np.cos(np.deg2rad(d['CAD_PitchY_deg'])),-1,1)))
 contact=np.flatnonzero((t>ls+.2)&(d['GroundForce_N']>1)&(d['FootClearance_m']<=0)) if ls>=0 else []
 ti=int(contact[0]) if len(contact) else None;touch=float(t[ti]) if ti is not None else None
 ds=meta.get('native_disarm_s');native_disarm=ds is not None
 arm_states=[v.get('ArmState') for v in records['ARM']]
 native_disarm_log=1 in arm_states and 0 in arm_states[arm_states.index(1)+1:]
 armed_after=[v for v in records['ARM'] if v.get('ArmState')==1]
 disarmed_after=[v for v in records['ARM'] if v.get('ArmState')==0 and armed_after and v['TimeUS']>armed_after[0]['TimeUS']]
 disarm_log_s=disarmed_after[0]['TimeUS']*1e-6 if disarmed_after else ds
 di=int(np.argmin(abs(t-disarm_log_s))) if disarm_log_s is not None else None
 premature=bool(native_disarm and (touch is None or disarm_log_s<touch-.1 or (d['FootClearance_m'][di]>.02 and d['GroundForce_N'][di]<1)))
 flight=t>=liftoff if liftoff is not None else np.zeros(len(t),bool)
 post=t>=touch if touch is not None else np.zeros(len(t),bool)
 tail=t>=t[-1]-1
 contacts=sum((d[f'Foot{k}Normal_N']>1).astype(int) for k in range(1,5))
 rebound=(d['FootClearance_m']>.005)&(d['GroundForce_N']<.5)&post
 hops=[];start=None
 for i,on in enumerate(rebound):
  if on and start is None:start=i
  if not on and start is not None:
   if t[i]-t[start]>=.02:hops.append([float(t[start]),float(t[i])])
   start=None
 if start is not None and t[-1]-t[start]>=.02:hops.append([float(t[start]),float(t[-1])])
 settled=bool(touch is not None and np.max(lean[tail])<3 and np.max(abs(d['VerticalSpeed_m_s'][tail]))<.03 and np.max(np.hypot(d['VX_m_s'][tail],d['VY_m_s'][tail]))<.03 and np.min(contacts[tail])>=3)
 tipped=bool(touch is not None and np.max(lean[post])>26)
 fan_stopped=np.flatnonzero((t>=disarm_log_s)&(d['GrossThrust_N']<.1)&(d['PWM5_us']<=1005)) if disarm_log_s is not None else []
 m={'case':name,'wind_world_ms':p['windWorld'],'gps_phase_rad':definition['gpsPhase'],'mass_kg':p['mass'],
 'ground_stiffness_N_m_per_foot':p['groundStiffness'],'ground_damping_Ns_m_per_foot':p['groundDamping'],
 'normal_arming_observed':meta['armed'],'native_mode_sequence':modes,'only_planned_modes':allowed,'native_land_entered':entered_land,
 'liftoff_s':liftoff,'hover_start_s':hs,'land_request_s':ls,'touchdown_s':touch,'native_disarm_s':disarm_log_s,'recording_end_s':float(t[-1]),
 'hover_completed':hover_complete,'hover_height_min_m':float(np.min(d['Height_m'][hover])) if hover_complete else None,
 'hover_height_max_m':float(np.max(d['Height_m'][hover])) if hover_complete else None,
 'height_pass':bool(hover_complete and np.max(abs(d['Height_m'][hover]-5))<=.1),
 'max_radius_m':float(np.max(radius)),'radius_1m_pass':bool(np.max(radius)<=1),'radius_at_touchdown_m':float(radius[ti]) if ti is not None else None,
 'radius_final_m':float(radius[-1]),'landing_duration_s':touch-ls if touch is not None else None,
 'airborne_duration_s':touch-liftoff if touch is not None and liftoff is not None else None,
 'touchdown_CG_vertical_speed_m_s':float(d['VerticalSpeed_m_s'][max(0,ti-1)]) if ti is not None else None,
 'touchdown_fastest_foot_vertical_speed_m_s':float(min(d[f'Foot{k}VZ_m_s'][max(0,ti-1)] for k in range(1,5))) if ti is not None else None,
 'touchdown_horizontal_speed_m_s':float(np.hypot(d['VX_m_s'][ti],d['VY_m_s'][ti])) if ti is not None else None,
 'touchdown_lean_deg':float(lean[ti]) if ti is not None else None,'peak_flight_lean_deg':float(np.max(lean[flight])) if np.any(flight) else None,
 'peak_post_contact_lean_deg':float(np.max(lean[post])) if np.any(post) else None,
 'peak_ground_load_N':float(np.max(d['GroundForce_N'][post])) if np.any(post) else None,
 'peak_ground_load_bodyweights':float(np.max(d['GroundForce_N'][post])/(p['mass']*p['g'])) if np.any(post) else None,
 'max_all_feet_rebound_clearance_m':max(0.,float(np.max(d['FootClearance_m'][post]))) if np.any(post) else None,
 'significant_hop_intervals_s':hops,'tipped_guard_26deg':tipped,'settled_last_second':settled,
 'native_disarm_observed':native_disarm,'native_disarm_dataflash':native_disarm_log,'premature_disarm':premature,
 'touchdown_to_disarm_s':disarm_log_s-touch if touch is not None and disarm_log_s is not None else None,
 'fan_below_point1N_s':float(t[fan_stopped[0]]) if len(fan_stopped) else None,
 'final_fan_thrust_N':float(d['GrossThrust_N'][-1]),'final_PWM5_us':float(d['PWM5_us'][-1]),
 'final_contact_count':int(contacts[-1]),'final_lean_deg':float(lean[-1]),
 'native_disarm_records':disarmed_after,'native_fusion_messages':[v.get('Message','') for v in records['MSG'] if any(s in v.get('Message','') for s in ['using GPS','Disarm','Thrust Loss'])]}
 phases={'climb':(t>=liftoff)&(t<hs) if liftoff is not None else np.zeros(len(t),bool),
 'hover':hover,'descent':(t>=ls)&(t<=touch) if touch is not None else np.zeros(len(t),bool),'after_touchdown':post}
 m['phase_max_radius_m']={k:float(np.max(radius[v])) if np.any(v) else None for k,v in phases.items()}
 pos_descent=[v for v in records['PSCN'] if touch is not None and ls+.5<=v['TimeUS']*1e-6<=touch-.2]
 m['native_horizontal_control_samples_during_descent']=len(pos_descent)
 m['native_landed_disarm_reason_verified']=bool(disarmed_after and disarmed_after[0].get('Method')==13 and not disarmed_after[0].get('Forced',0))
 airborne=(t>=liftoff)&(t<=touch) if touch is not None and liftoff is not None else flight
 m['max_airborne_radius_m']=float(np.max(radius[airborne])) if np.any(airborne) else None
 crossed=np.flatnonzero(radius>1)
 if len(crossed):
  ci=int(crossed[0]);when=float(t[ci]);phase='preflight' if liftoff is None or when<liftoff else ('climb' if when<hs else ('hover' if when<ls else ('descent' if touch is None or when<touch else 'after_touchdown')))
  m['first_1m_crossing']={'sim_s':when,'after_liftoff_s':when-liftoff if liftoff is not None else None,'phase':phase}
 else:m['first_1m_crossing']=None
 m['landing_model_pass']=bool(touch is not None and entered_land and native_disarm and native_disarm_log and m['native_landed_disarm_reason_verified'] and len(pos_descent)>10 and not premature and settled and not tipped and not hops and len(fan_stopped)>0 and abs(m['touchdown_fastest_foot_vertical_speed_m_s'])<=.5)
 m['mission_pass']=bool(hover_complete and m['height_pass'] and m['radius_1m_pass'] and m['landing_model_pass'] and allowed and m['peak_flight_lean_deg']<=12)
 (f/'flight_metrics.json').write_text(json.dumps(m,indent=2));return m
if __name__=='__main__':
 for name in sys.argv[1:]:print(json.dumps(analyse(name),indent=2))
