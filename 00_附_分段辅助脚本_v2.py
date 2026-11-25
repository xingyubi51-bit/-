"""把手写整章稿格式化成仓库格式：BOM、CRLF、每段两个全角空格；超过 86 字的段在句末标点处拆开，不改字。"""
import sys,glob,os,re
# 用法：python3 00_附_分段辅助脚本_v2.py 手写稿目录 输出目录 仓库目录
# 手写稿目录里放 29.txt、30.txt……（第一行标题，段间空一行）；仓库目录用来取原文件名。
SRC,DST,REPO=sys.argv[1],sys.argv[2],sys.argv[3]
os.makedirs(DST,exist_ok=True)
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
import math
LIM=86
def split_para(p):
    if len(p)<=LIM: return [p]
    ss=sentences(p)
    k=math.ceil(len(p)/LIM); target=len(p)/k
    pieces=[];cur=''
    for s_ in ss:
        if cur and (len(cur)+len(s_)>LIM or len(cur)>=target):
            pieces.append(cur);cur=s_
        else: cur+=s_
    if cur: pieces.append(cur)
    res=[];openq=False
    for pc in pieces:
        if openq: pc='“'+pc
        o=pc.count('“')-pc.count('”')
        openq=o>0
        if openq: pc=pc+'”'
        res.append(pc)
    return res
for f in sorted(glob.glob(SRC+'/*.txt')):
    n=os.path.basename(f)[:-4]
    raw=open(f,encoding='utf-8').read().strip().replace('\r','')
    parts=[p.strip().replace('\n','') for p in re.split(r'\n\s*\n',raw) if p.strip()]
    title=parts[0]; body=[]
    for p in parts[1:]: body+=split_para(p)
    name=os.path.basename(glob.glob(f'{REPO}/{int(n):02d}_第*.txt')[0])
    out='\ufeff'+title+'\r\n\r\n'+'\r\n\r\n'.join('\u3000\u3000'+p for p in body)+'\r\n'
    open(f'{DST}/{name}','w',encoding='utf-8',newline='').write(out)
    print('ok',name,len(''.join(body)))
