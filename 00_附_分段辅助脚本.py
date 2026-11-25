import sys,glob,os,re,math
LIM=78
def sentences(p):
    out=[];cur=''
    i=0
    while i<len(p):
        cur+=p[i]
        if p[i] in '。！？' :
            j=i+1
            while j<len(p) and p[j] in '”』」’…':
                cur+=p[j]; j+=1
            i=j-1
            out.append(cur);cur=''
        i+=1
    if cur: out.append(cur)
    return out
def split_para(p):
    if len(p)<=LIM: return [p]
    ss=sentences(p)
    k=math.ceil(len(p)/LIM); target=len(p)/k
    pieces=[];cur=''
    for s in ss:
        if cur and (len(cur)+len(s)>LIM or len(cur)>=target):
            pieces.append(cur);cur=s
        else: cur+=s
    if cur: pieces.append(cur)
    res=[];openq=False
    for pc in pieces:
        if openq: pc='“'+pc
        o=pc.count('“')-pc.count('”')
        openq = o>0
        if openq: pc=pc+'”'
        res.append(pc)
    return res
for n in sys.argv[1:]:
    raw=open('work/raw/%s.txt'%n,encoding='utf-8').read().strip().replace('\r','')
    parts=[p.strip().replace('\n','') for p in re.split(r'\n\s*\n',raw) if p.strip()]
    title=parts[0]; body=[]
    for p in parts[1:]: body+=split_para(p)
    name=os.path.basename(glob.glob('/tmp/novel/%s_第*'%n)[0])
    out='\ufeff'+title+'\r\n\r\n'+'\r\n\r\n'.join('\u3000\u3000'+p for p in body)+'\r\n'
    open('work/final/'+name,'w',encoding='utf-8',newline='').write(out)
    print('ok',name)
