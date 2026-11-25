import sys,glob,os,re,math
REPO='/tmp/src_repo'; OUT='/tmp/work/out'; SRC='/app/work/b'
LIM=88
REPL=[('与我无关','跟我没关系'),('与你无关','跟你没关系'),('多谢','谢谢'),('此刻','这会儿'),('须得','得'),('沈敬信','沈敬'),('二十一年','二十年'),('老身','我'),('春水刀','刀'),('明月剑阁','剑阁')]
def sentences(p):
    out=[];cur='';i=0
    while i<len(p):
        cur+=p[i]
        if p[i] in '。！？':
            j=i+1
            while j<len(p) and p[j] in '”』」’…':
                cur+=p[j]; j+=1
            i=j-1; out.append(cur); cur=''
        i+=1
    if cur: out.append(cur)
    return out
def split_para(p):
    if len(p)<=LIM: return [p]
    ss=sentences(p); k=math.ceil(len(p)/LIM); target=len(p)/k
    pieces=[];cur=''
    for s in ss:
        if cur and (len(cur)+len(s)>LIM or len(cur)>=target):
            pieces.append(cur);cur=s
        else: cur+=s
    if cur: pieces.append(cur)
    res=[];openq=False
    for pc in pieces:
        if openq: pc='“'+pc
        o=pc.count('“')-pc.count('”'); openq=o>0
        if openq: pc=pc+'”'
        res.append(pc)
    return res
chap={}
for f in sorted(glob.glob(SRC+'/*.txt')):
    t=open(f,encoding='utf-8').read().replace('\r','')
    for blk in re.split(r'(?m)^@@(\d+)\s*$',t)[1:]  if False else []: pass
    parts=re.split(r'(?m)^@@(\d+)\s*$',t)
    for i in range(1,len(parts),2):
        chap[int(parts[i])]=parts[i+1].strip()
rows=[];tot=0
for n in sorted(chap):
    raw=chap[n]
    for a,b in REPL: raw=raw.replace(a,b)
    ps=[p.strip().replace('\n','') for p in re.split(r'\n\s*\n',raw) if p.strip()]
    title=ps[0]; body=[]
    for p in ps[1:]: body+=split_para(p)
    targets=sorted(glob.glob(f'{REPO}/{n}_第*.txt')); assert targets,n
    name=os.path.basename(targets[0])
    open(f'{OUT}/{name}','w',encoding='utf-8',newline='').write('\ufeff'+title+'\r\n\r\n'+'\r\n\r\n'.join('\u3000\u3000'+p for p in body)+'\r\n')
    txt=''.join(body); L=len(txt); tot+=L
    q1=txt.count('“');q2=txt.count('”')
    bs=len(re.findall('不是[^。]{0,20}是',txt))
    # runs of short sentences inside one paragraph
    run=0
    for p in body:
        ss=[s for s in sentences(p) if s]
        c=0
        for s in ss:
            if len(s)<=8: c+=1
            else: c=0
            if c>=4: run+=1;break
    stale=[w for w in ['与我无关','沈敬信','二十一年','多谢','此刻','老身','春水刀','须得','先帝'] if w in txt]
    rows.append((n,L,len(body),L//len(body),max(len(p) for p in body),'' if q1==q2 else f'引号{q1}/{q2}',f'不是是{bs}' if bs>1 else '',f'碎句{run}' if run else '',','.join(stale)))
for r in rows: print(*r)
print('chapters',len(rows),'chars',tot)
