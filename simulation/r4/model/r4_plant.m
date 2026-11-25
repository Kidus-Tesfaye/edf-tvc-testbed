function [dx, aux] = r4_plant(x, act, t, P)
% Nonlinear six-degree-of-freedom rigid body, quaternion attitude, fan and
% servo dynamics. CAD X/Y are transverse; CAD +Z is upward thrust.
pos=x(1:3);vel=x(4:6);q=x(7:10);qn=q/max(norm(q),1e-12);
w=qn(1);a=qn(2);b=qn(3);c=qn(4);
R=[1-2*(b*b+c*c),2*(a*b-w*c),2*(a*c+w*b);...
   2*(a*b+w*c),1-2*(a*a+c*c),2*(b*c-w*a);...
   2*(a*c-w*b),2*(b*c+w*a),1-2*(a*a+b*b)];
omega=x(11:13);T=max(0,x(14));delta=max(-P.deltaMax,min(P.deltaMax,x(15:18)));
v=1+(P.voltageFinalScale-1)*max(0,min(1,(t-P.voltageStart)/max(P.voltageRamp,0.01)));
Tmax=P.TmaxNominal*P.thrustScale*v;
throttle=max(0,min(1,act(1)));
Ttarget=Tmax*((1-P.throttleExpo)*throttle+P.throttleExpo*throttle^2);
dT=(Ttarget-x(14))/P.fanTau;
deltaTarget=max(-P.deltaMax,min(P.deltaMax,act(2:5)));
ddelta=max(-P.servoRate,min(P.servoRate,(deltaTarget-x(15:18))/P.servoTau));
cl=P.CLalpha*delta./sqrt(1+(delta/P.stallAngle).^4);
qS=T/(2*P.jetArea)*P.vaneArea*P.effectiveness;
fv=qS*cl;drag=qS*(P.CD0+P.inducedDragK*cl.^2);
forceBody=[0;0;T];tau=cross([-P.cg(1);-P.cg(2);0],[0;0;T]);
for k=1:4
    phi=(k-1)*pi/2;tanvec=[-sin(phi);cos(phi);0];
    ff=tanvec*fv(k)+[0;0;-drag(k)];
    arm=[P.vaneRadius*cos(phi);P.vaneRadius*sin(phi);P.forceZ]-P.cg;
    forceBody=forceBody+ff;tau=tau+cross(arm,ff);
end
tau=tau+[0;0;P.residualTorquePerN*T]-P.angularDrag.*omega;
airVelocity=vel-P.windWorld;
forceWorld=R*forceBody-[0;0;P.mass*P.g]-P.linearDrag.*airVelocity-P.quadraticDrag.*abs(airVelocity).*airVelocity;
for n=1:2
    if t>=P.pulseTimes(n,1) && t<P.pulseTimes(n,2)
        forceWorld=forceWorld+P.forceDisturbance(:,n);tau=tau+P.torqueDisturbance(:,n);
    end
end
maxTension=0;ropeForce=zeros(3,1);groundForce=0;
if P.tetherEnabled>0.5
    for k=1:4
        rb=P.eyeBody(:,k);eye=pos+R*rb;eyeVelocity=vel+R*cross(omega,rb);
        for j=1:2
            if j==1,anchor=P.upperAnchor(:,k);L=P.upperLength;
            else,anchor=P.lowerAnchor(:,k);L=P.lowerLength;end
            diff=anchor-eye;d=norm(diff);dir=diff/max(d,1e-12);excess=d-L;
            if excess>0
                extensionRate=-dot(eyeVelocity,dir);
                tension=max(0,P.tetherStiffness*excess+P.tetherDamping*extensionRate);
                ff=tension*dir;forceWorld=forceWorld+ff;ropeForce=ropeForce+ff;
                tau=tau+cross(rb,R'*ff);maxTension=max(maxTension,tension);
            end
        end
    end
end
if P.groundEnabled>0.5
    for k=1:4
        rb=P.feetBody(:,k);foot=pos+R*rb;vv=vel+R*cross(omega,rb);
        if foot(3)<P.floorZ
            fn=max(0,P.groundStiffness*(P.floorZ-foot(3))-P.groundDamping*vv(3));
            ft=-P.groundFriction*fn*tanh(vv(1:2)/0.03);ff=[ft;fn];
            forceWorld=forceWorld+ff;tau=tau+cross(rb,R'*ff);groundForce=groundForce+fn;
        end
    end
end
pp=omega(1);qq=omega(2);rr=omega(3);
Q=[0,-pp,-qq,-rr;pp,0,rr,-qq;qq,-rr,0,pp;rr,qq,-pp,0];
dq=0.5*Q*q+0.5*(1-dot(q,q))*q;
angularAcceleration=(tau-cross(omega,P.inertia.*omega))./P.inertia;
dx=[vel;forceWorld/P.mass;dq;angularAcceleration;dT;ddelta];
cllim=P.CLalpha*P.deltaMax/sqrt(1+(P.deltaMax/P.stallAngle)^4);
spinMargin=4*P.vaneRadius*qS*cllim-abs(P.residualTorquePerN*T);
aux=[fv;forceBody(3);sum(drag);Tmax;maxTension;groundForce;tau;norm(ropeForce);...
     spinMargin;norm(q)-1;P.mass*P.g];
end

