function done=r4_mission_supervise(x,t)
% Mission observation/phase command only. No true XY is fed to the controller.
global R4_MISSION_OUTDIR R4_MISSION_STATE R4_AP_PARAMETERS
persistent settleBegin hoverBegin landRequest disarmObserved lastRead
if isempty(settleBegin) || t==0
 settleBegin=-1;hoverBegin=-1;landRequest=-1;disarmObserved=-1;lastRead=-1;
 R4_MISSION_STATE=struct('hover_start_s',-1,'land_requested',false,'land_request_sim_s',-1,'native_disarm_observed_sim_s',-1,'mission_recording_complete',false);
end
changed=false;done=false;
if hoverBegin<0
 if abs(x(3)-5)<=.1 && abs(x(6))<=.1
  if settleBegin<0,settleBegin=t;end
  if t-settleBegin>=1,hoverBegin=t;R4_MISSION_STATE.hover_start_s=t;changed=true;end
 else,settleBegin=-1;
 end
end
if hoverBegin>=0 && landRequest<0 && t>=hoverBegin+8
 landRequest=t;R4_MISSION_STATE.land_requested=true;R4_MISSION_STATE.land_request_sim_s=t;changed=true;
 fprintf('MISSION full hover complete; request native LAND at %.3f s\n',t);
end
if landRequest>=0 && t-lastRead>=.0999
 lastRead=t;path=fullfile(R4_MISSION_OUTDIR,'native_status.json');
 if isfile(path)
  try
   S=jsondecode(fileread(path));
   if S.had_armed && ~S.armed && disarmObserved<0
    disarmObserved=t;R4_MISSION_STATE.native_disarm_observed_sim_s=t;R4_MISSION_STATE.height_when_disarm_observed_m=x(3);changed=true;
   end
  catch
  end
 end
end
if disarmObserved>=0 && t>=disarmObserved+5
 done=true;R4_MISSION_STATE.mission_recording_complete=true;R4_MISSION_STATE.recording_end_s=t;changed=true;
end
if changed
 path=fullfile(R4_MISSION_OUTDIR,'mission_status.json');tmp=[path '.tmp'];
 fid=fopen(tmp,'w');fprintf(fid,'%s',jsonencode(R4_MISSION_STATE,'PrettyPrint',true));fclose(fid);
 ok=false;
 for attempt=1:20
  [ok,why]=movefile(tmp,path,'f');if ok,break;end
  pause(.005);
 end
 if ~ok,error('Mission status publish failed: %s',why);end
end
end
