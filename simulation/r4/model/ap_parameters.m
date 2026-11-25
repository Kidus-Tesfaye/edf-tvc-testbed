function P=ap_parameters(name)
if nargin<1,name='calm';end
folder=fileparts(mfilename('fullpath'));root=fileparts(folder);
P=jsondecode(fileread(fullfile(folder,'design_parameters.json')));
P.dt=1/2400;P.linkTs=1/1200;P.stopTime=300;P.startupEnabled=1;P.tetherEnabled=0;P.zReference=5;
P.initialEuler=zeros(3,1);P.x0=zeros(18,1);P.x0(7)=1;
P.forceDisturbance=zeros(3,2);P.torqueDisturbance=zeros(3,2);P.pulseTimes=[95,95.2;105,105.5];
P.rangeNoiseStd=.002;P.rangeBias=0;P.rangeSensorBodyZ=P.floorZ+.13;P.rngSeed=2107;
C=jsondecode(fileread(fullfile(root,'config','cases.json')));i=find(strcmp({C.name},name),1);
assert(~isempty(i),'Unknown stress case');S=C(i);
P.mass=P.mass*S.massScale;P.inertia=P.inertia*S.massScale;
P.thrustScale=S.thrustScale;P.servoTau=P.servoTau*S.servoLagScale;P.servoRate=P.servoRate*S.servoRateScale;
P.windWorld=S.windWorld(:);P.rngSeed=S.seed;
P.groundStiffness=P.groundStiffness*S.groundStiffnessScale;P.groundDamping=P.groundDamping*S.groundDampingScale;
if isfield(S,'rangeNoiseStd'),P.rangeNoiseStd=S.rangeNoiseStd;end
if isfield(S,'rangeBias'),P.rangeBias=S.rangeBias;end
P.jsonPort=9002;
end
