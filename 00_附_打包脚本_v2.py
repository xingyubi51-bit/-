import sys,glob,os,re,math
# 用法：python3 00_附_打包脚本_v2.py 手写稿目录 仓库目录 输出目录
SRC,REPO,OUT=sys.argv[1:4]
os.makedirs(OUT,exist_ok=True)
LIM=86
KEEP={148:'屋脊上的酒',152:'对铃说的假话',161:'令在案上'}
REPL=[('与我无关','跟我没关系'),('多谢','谢谢'),('明月剑阁','剑阁')]
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
    for s_ in ss:
        if cur and (len(cur)+len(s_)>LIM or len(cur)>=target):
            pieces.append(cur);cur=s_
        else: cur+=s_
    if cur: pieces.append(cur)
    res=[];openq=False
    for pc in pieces:
        if openq: pc='“'+pc
        o=pc.count('“')-pc.count('”'); openq=o>0
        if openq: pc=pc+'”'
        res.append(pc)
    return res
def presplit(p):
    # 单句≥80字且无句号可拆时，在引号外最接近中点的逗号/分号处断句
    for _ in range(4):
        done=True
        for sent in re.findall(r'[^。！？]+[。！？]*[”』」’…]*',p):
            if len(sent)>=80:
                inq=False;c=[]
                for k,ch in enumerate(sent):
                    if ch=='“':inq=True
                    elif ch=='”':inq=False
                    elif ch in '，；' and not inq and 12<k<len(sent)-12: c.append(k)
                if c:
                    k=min(c,key=lambda x:abs(x-len(sent)/2))
                    p=p.replace(sent,sent[:k]+'。'+sent[k+1:],1);done=False;break
        if done:break
    return p
for old in glob.glob(OUT+'/*.txt'): os.remove(old)
for f in sorted(glob.glob(SRC+'/*.txt'),key=lambda x:int(os.path.basename(x)[:-4])):
    n=int(os.path.basename(f)[:-4])
    raw=open(f,encoding='utf-8').read().strip().replace('\r','')
    for a,b in REPL: raw=raw.replace(a,b)
    parts=[p.strip().replace('\n','') for p in re.split(r'\n\s*\n',raw) if p.strip()]
    title=parts[0]; body=[]
    for p in parts[1:]: body+=split_para(presplit(p))
    targets=sorted(glob.glob(f'{REPO}/{n}_第*.txt'))
    assert targets,n
    if n in KEEP:
        targets=[t for t in targets if KEEP[n] in t]; assert targets,n
    for t in targets:
        name=os.path.basename(t)
        out='\ufeff'+title+'\r\n\r\n'+'\r\n\r\n'.join('\u3000\u3000'+p for p in body)+'\r\n'
        open(f'{OUT}/{name}','w',encoding='utf-8',newline='').write(out)
print('done',len(os.listdir(OUT)))
