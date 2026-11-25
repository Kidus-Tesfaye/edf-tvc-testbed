function run_ap_case(name,outdir)
folder=fileparts(mfilename('fullpath'));addpath(folder,fullfile(folder,'..','runtime','connector'));cd(folder);
global R4_AP_PARAMETERS R4_HORIZONTAL_SENSOR_CONFIG R4_GPS_SENSOR_LOG R4_FLOW_SENSOR_LOG R4_MISSION_OUTDIR R4_MISSION_STATE
root=fileparts(folder);
C=jsondecode(fileread(fullfile(root,'config','cases.json')));R4_HORIZONTAL_SENSOR_CONFIG=C(find(strcmp({C.name},name),1));
G=jsondecode(fileread(fullfile(root,'config','gps_noise.json')));
if isfield(G,R4_HORIZONTAL_SENSOR_CONFIG.profile),R4_HORIZONTAL_SENSOR_CONFIG.gps=G.(R4_HORIZONTAL_SENSOR_CONFIG.profile);end
R4_GPS_SENSOR_LOG=[];R4_FLOW_SENSOR_LOG=[];R4_MISSION_OUTDIR=outdir;R4_MISSION_STATE=[];clear r4_mission_supervise;
P=ap_parameters(name);R4_AP_PARAMETERS=P;r4_ap_close;clear r4_ap_receive r4_ap_send;
cleanup=onCleanup(@r4_ap_close);
assert(isfile('R4_ArduPilot_JSON.slx'),'Missing model file. Extract the complete package.');
mdl='R4_ArduPilot_JSON';load_system(mdl);mw=get_param(mdl,'ModelWorkspace');assignin(mw,'P',P);assignin(mw,'V',ap_pack(P));
notes=find_system(mdl,'FindAll','on','Type','annotation');
for h=notes(:)'
    obj=get_param(h,'Object');
    obj.Text=strrep(obj.Text,'hover 8 s; no landing.','hover 8 s; native LAND and automatic disarm.');
    obj.Text=strrep(obj.Text,'Observer stops logging only.','Observer sequences LAND after the hover and stops 5 s after native disarm.');
    obj.Text=strrep(strrep(obj.Text,'400 Hz lockstep link; 0.5 ms physics step;','1200 Hz lockstep link; 1/2400 s physics step;'),'R4 with tether/guard.','R4 stress plant; fixed controller; rope forces disabled.');
end
rt=sfroot;ch=rt.find('-isa','Stateflow.EMChart','Path',[mdl '/Mission completion observer']);
ch.Script=sprintf('function done=observe(x,t)\ncoder.extrinsic(''r4_mission_supervise'');\ndone=false;done=r4_mission_supervise(x,t);\nend\n');
ch.ChartUpdate='DISCRETE';ch.SampleTime=num2str(1/R4_HORIZONTAL_SENSOR_CONFIG.observerHz,'%.16g');
if getSimulinkBlockHandle([mdl '/End after eight seconds of hover'])>0,set_param([mdl '/End after eight seconds of hover'],'Name','End five seconds after native disarm');end
save_system(mdl);
out=sim(mdl,'StopTime',num2str(P.stopTime));
t=out.statesLog.Time;x=aligned(out.statesLog);pwm=aligned(out.pwmLog);act=aligned(out.actuatorLog);forces=aligned(out.forcesLog);
q=x(:,7:10)./vecnorm(x(:,7:10),2,2);w=q(:,1);a=q(:,2);b=q(:,3);c=q(:,4);
angles=[atan2(2*(w.*a+b.*c),1-2*(a.^2+b.^2)),asin(max(-1,min(1,2*(w.*b-c.*a)))),atan2(2*(w.*c+a.*b),1-2*(b.^2+c.^2))];
rz=[2*(a.*c-w.*b),2*(b.*c+w.*a),1-2*(a.^2+b.^2)];
feetClearance=x(:,3)+rz*P.feetBody-P.floorZ;clearance=min(feetClearance,[],2);
feetForce=zeros(numel(t),4);feetVZ=zeros(numel(t),4);
for j=1:4
 rb=P.feetBody(:,j);om=x(:,11:13);
 cv=[om(:,2)*rb(3)-om(:,3)*rb(2),om(:,3)*rb(1)-om(:,1)*rb(3),om(:,1)*rb(2)-om(:,2)*rb(1)];
 feetVZ(:,j)=x(:,6)+sum(rz.*cv,2);
 feetForce(:,j)=max(0,-P.groundStiffness*feetClearance(:,j)-P.groundDamping*feetVZ(:,j)).*(feetClearance(:,j)<0);
end
T=table(t,x(:,3),x(:,6),rad2deg(angles(:,1)),rad2deg(angles(:,2)),rad2deg(unwrap(angles(:,3))),...
 x(:,1),x(:,2),x(:,14),act(:,1),forces(:,8),forces(:,9),clearance,...
 'VariableNames',{'Time_s','Height_m','VerticalSpeed_m_s','CAD_RollX_deg','CAD_PitchY_deg','CAD_SpinZ_deg',...
 'X_m','Y_m','GrossThrust_N','Throttle_0to1','MaxLineTension_N','GroundForce_N','FootClearance_m'});
for k=1:4,T.(sprintf('Vane%d_deg',k))=rad2deg(x(:,14+k));T.(sprintf('PWM%d_us',k))=pwm(:,k);end
for j=1:4
 T.(sprintf('Foot%dClearance_m',j))=feetClearance(:,j);T.(sprintf('Foot%dNormal_N',j))=feetForce(:,j);T.(sprintf('Foot%dVZ_m_s',j))=feetVZ(:,j);
end
T.BodyOmegaX_rad_s=x(:,11);T.BodyOmegaY_rad_s=x(:,12);T.BodyOmegaZ_rad_s=x(:,13);
T.PWM5_us=pwm(:,5);T.VX_m_s=x(:,4);T.VY_m_s=x(:,5);
writetable(T,fullfile(outdir,'physics.csv'));
if ~isempty(R4_GPS_SENSOR_LOG)
 GT=array2table(R4_GPS_SENSOR_LOG,'VariableNames',{'Time_s','TrueN_m','TrueE_m','ErrorN_m','ErrorE_m'});
 writetable(GT,fullfile(outdir,'gps_sensor_samples.csv'));
end
if ~isempty(R4_FLOW_SENSOR_LOG)
 FT=array2table(R4_FLOW_SENSOR_LOG,'VariableNames',{'SampleTime_s','SendTime_s','FlowX_rad_s','FlowY_rad_s','TrueGyroX_rad_s','TrueGyroY_rad_s','TrueRange_m','NoiseX_rad_s','NoiseY_rad_s'});
 writetable(FT,fullfile(outdir,'flow_sensor_samples.csv'));
end
SC=R4_HORIZONTAL_SENSOR_CONFIG;save(fullfile(outdir,'sensor_configuration.mat'),'SC');
save(fullfile(outdir,'physics.mat'),'P','t','x','pwm','act','forces','angles','clearance','-v7.3');
fid=fopen(fullfile(outdir,'plant_parameters.json'),'w');fprintf(fid,'%s',jsonencode(P,'PrettyPrint',true));fclose(fid);
close_system(mdl,0);fprintf('AP_CASE_COMPLETED %s\n',name);
end
function v=aligned(ts)
v=squeeze(ts.Data);if size(v,1)~=numel(ts.Time),v=v.';end
end
