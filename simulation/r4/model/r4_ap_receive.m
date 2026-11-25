function pwm=r4_ap_receive(t)
% Official JSON UDP protocol. Busy-poll host socket; still wait for every frame.
% No change to timestamps, controller, physics, sensor rate or packet contents.
global R4_UDP_SOCKET R4_AP_PARAMETERS
persistent lastFrame connected startTimer frames
if isempty(R4_UDP_SOCKET) || t==0
    r4_ap_close;
    R4_UDP_SOCKET=pnet('udpsocket',R4_AP_PARAMETERS.jsonPort);
    pnet(R4_UDP_SOCKET,'setreadtimeout',.1);pnet(R4_UDP_SOCKET,'setwritetimeout',1);
    lastFrame=-1;connected=false;startTimer=tic;frames=0;
end
while true
    n=pnet(R4_UDP_SOCKET,'readpacket',40,'noblock');
    if n==40
        magic=pnet(R4_UDP_SOCKET,'read',1,'UINT16','intel');
        rate=double(pnet(R4_UDP_SOCKET,'read',1,'UINT16','intel'));
        frame=double(pnet(R4_UDP_SOCKET,'read',1,'UINT32','intel'));
        values=double(pnet(R4_UDP_SOCKET,'read',16,'UINT16','intel'))';
        [ip,port]=pnet(R4_UDP_SOCKET,'gethost');
        if magic~=18458 || ~isequal(double(ip(:))',[127 0 0 1]),continue;end
        if frame==lastFrame,continue;end
        if frame<lastFrame,error('ArduPilot restarted during a test.');end
        if connected && frame~=lastFrame+1,error('Lost ArduPilot frame: %d -> %d',lastFrame,frame);end
        if ~connected,fprintf('AP_JSON_CONNECTED localhost:%d, %g Hz\n',port,rate);connected=true;end
        lastFrame=frame;pwm=values;frames=frames+1;startTimer=tic;
        if mod(frames,4000)==0,fprintf('AP_JSON t=%.1f s, frame=%d\n',t,frame);end
        return;
    end
    if toc(startTimer)>90,error('ArduPilot JSON input timeout.');end
end
end
