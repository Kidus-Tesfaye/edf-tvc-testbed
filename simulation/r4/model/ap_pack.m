function [V,code]=ap_pack(P)
names=fieldnames(P);V=zeros(0,1);code='';
for k=1:numel(names)
    n=names{k};v=P.(n);i=numel(V)+1;V=[V;double(v(:))];j=numel(V);
    if isscalar(v),s=sprintf('P.%s=V(%d);\n',n,i);
    else,s=sprintf('P.%s=reshape(V(%d:%d),%d,%d);\n',n,i,j,size(v,1),size(v,2));end
    code=[code s];
end
end
