function r4_ap_send(x,dx,t)
global R4_UDP_SOCKET R4_AP_PARAMETERS R4_HORIZONTAL_SENSOR_CONFIG R4_GPS_SENSOR_LOG R4_FLOW_SOCKET R4_FLOW_SENSOR_LOG
P=R4_AP_PARAMETERS;H=R4_HORIZONTAL_SENSOR_CONFIG;
persistent range lastRangeTime gpsLastTime gpsError gpsStream flowLastTick flowLastSample flowSum flowGyroSum flowDuration flowQueue flowStream
if isempty(lastRangeTime) || t==0,lastRangeTime=-1;range=.13;rng(P.rngSeed);end
q=x(7:10)/norm(x(7:10));w=q(1);a=q(2);b=q(3);c=q(4);
R=[1-2*(b*b+c*c),2*(a*b-w*c),2*(a*c+w*b);...
 2*(a*b+w*c),1-2*(a*a+c*c),2*(b*c-w*a);...
 2*(a*c-w*b),2*(b*c+w*a),1-2*(a*a+b*b)];
S=diag([1,-1,-1]);
J.timestamp=t;J.imu.gyro=S*x(11:13);
J.imu.accel_body=S*(R'*(dx(4:6)+[0;0;P.g]));
J.position=S*x(1:3);J.position(3)=J.position(3)+P.floorZ;J.velocity=S*x(4:6);
% Native optical-flow AGL includes physical CG-to-floor height; no force/IMU change.
if isfield(H,'gps')
 if isempty(gpsLastTime) || t==0
  gpsLastTime=-1;gpsError=zeros(2,1);gpsStream=RandStream('mt19937ar','Seed',P.rngSeed+911);
 end
 G=H.gps;phase=H.gpsPhase;
 if t-gpsLastTime>=1/G.rateHz-1e-7
  gpsError=G.whiteStdM*randn(gpsStream,2,1)+G.biasAmplitudeM*[sin(2*pi*t/G.periodN+phase);sin(2*pi*t/G.periodE+phase+.7)];
  gpsLastTime=t;R4_GPS_SENSOR_LOG(end+1,:)=[t,J.position(1:2)',gpsError'];
 end
 J.position(1:2)=J.position(1:2)+gpsError;
end
J.quaternion=[q(1);q(2);-q(3);-q(4)];
% This pinned SIM_JSON revision's range-copy loop still tests bit 7 for
% range 1. Supplying Euler as well as quaternion keeps that path populated;
% the documented protocol gives quaternion priority for actual attitude.
J.attitude=[atan2(2*(w*a+b*c),1-2*(a*a+b*b));...
 -asin(max(-1,min(1,2*(w*b-c*a))));-atan2(2*(w*c+a*b),1-2*(b*b+c*c))];
if t-lastRangeTime>=.00999
    sensorZ=x(3)+R(3,3)*P.rangeSensorBodyZ;
    range=max(.05,(sensorZ-P.floorZ)/max(.2,R(3,3))+P.rangeBias+P.rangeNoiseStd*randn);
    lastRangeTime=t;
end
J.rng_1=range;J.battery.voltage=22.2;J.battery.current=0;

% A physical camera's image angular rate, using the actual floor and sensor
% offset. This is sensor emulation only; no position/velocity command is sent.
if isfield(H,'flow')
 if isempty(flowLastTick) || t==0
  flowLastTick=t;flowLastSample=t;flowSum=zeros(2,1);flowGyroSum=zeros(3,1);flowDuration=0;flowQueue={};
  flowStream=RandStream('mt19937ar','Seed',P.rngSeed+621);
  R4_FLOW_SOCKET=pnet('udpsocket',0);
 end
 F=H.flow;step=t-flowLastTick;flowLastTick=t;
 trueRange=max(.05,(x(3)+R(3,3)*P.rangeSensorBodyZ-P.floorZ)/max(.2,R(3,3)));
 gyro=S*x(11:13);vb=S*(R'*x(4:6))+cross(gyro,[0;0;.20304]);
 imageRate=[-vb(2)/trueRange+gyro(1);vb(1)/trueRange+gyro(2)];
 flowSum=flowSum+imageRate*step;flowGyroSum=flowGyroSum+gyro*step;flowDuration=flowDuration+step;
 if t-flowLastSample>=1/F.rateHz-1e-7
  noise=F.noiseAmplitudeRadS*(2*rand(flowStream,2,1)-1);measured=flowSum/flowDuration+noise;
  pkt.sampleTime=t;pkt.flowX=measured(1);pkt.flowY=measured(2);pkt.quality=200;
  pkt.gyro=flowGyroSum/flowDuration;pkt.trueRange=trueRange;pkt.noise=noise;
  flowQueue{end+1}=pkt;
  if numel(flowQueue)>F.delayFrames
   sent=flowQueue{1};flowQueue(1)=[];
   pnet(R4_FLOW_SOCKET,'printf',jsonencode(sent));pnet(R4_FLOW_SOCKET,'writepacket','127.0.0.1',9450+P.jsonPort-9002);
   R4_FLOW_SENSOR_LOG(end+1,:)=[sent.sampleTime,t,sent.flowX,sent.flowY,sent.gyro(1),sent.gyro(2),sent.trueRange,sent.noise'];
  end
  flowLastSample=t;flowSum=zeros(2,1);flowGyroSum=zeros(3,1);flowDuration=0;
 end
end

if abs(t/10-round(t/10))<1e-8
    fprintf('TRUTH t=%.1f h=%.4f m, RP/Y=%.2f %.2f %.2f deg, T=%.2f N\n',t,x(3),rad2deg(J.attitude),x(14));
end
pnet(R4_UDP_SOCKET,'printf',sprintf('\n%s\n',jsonencode(J)));
pnet(R4_UDP_SOCKET,'writepacket');
end
