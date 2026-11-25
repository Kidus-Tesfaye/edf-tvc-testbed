function r4_ap_close
global R4_UDP_SOCKET R4_FLOW_SOCKET
if ~isempty(R4_UDP_SOCKET)
    try,pnet(R4_UDP_SOCKET,'close');catch,end
end
R4_UDP_SOCKET=[];
if ~isempty(R4_FLOW_SOCKET)
 try,pnet(R4_FLOW_SOCKET,'close');catch,end
 R4_FLOW_SOCKET=[];
end
end
