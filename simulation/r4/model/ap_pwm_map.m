function act=ap_pwm_map(pwm, P)
% AP FRD axes correspond to CAD [X,-Y,-Z]. Front/right/back/left vanes
% are CAD +X/-Y/-X/+Y. Physical positive deflection is CAD tangent +phi.
act=zeros(5,1);act(1)=max(0,min(1,(pwm(5)-1000)/1000));
channel=[1,4,3,2];
for k=1:4
    value=pwm(channel(k));
    if value<900,value=1500;end % no valid pulse during firmware initialization
    act(k+1)=max(-1,min(1,(value-1500)/500))*P.deltaMax;
end
end
