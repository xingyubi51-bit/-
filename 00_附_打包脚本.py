#!/usr/bin/env python3
"""打包脚本：把 work/src/N.txt 手写稿格式化成仓库格式，输出到 out/chapters，并生成 zip。
用法：python3 pack.py SRC REPO OUT
- 超过86字的段在句号/问号/叹号处拆开(不改字)；BOM+CRLF+每段两个全角空格。
- 同号多文件(如111、130)：对每个仓库同号文件都输出一份，保留各自原标题行。
"""
import sys,glob,os,re,math
SRC,REPO,OUT=sys.argv[1:4]
os.makedirs(OUT,exist_ok=True)
LIM=86
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
for f in sorted(glob.glob(SRC+'/*.txt'),key=lambda x:int(os.path.basename(x)[:-4])):
    n=int(os.path.basename(f)[:-4])
    raw=open(f,encoding='utf-8').read().strip().replace('\r','')
    parts=[p.strip().replace('\n','') for p in re.split(r'\n\s*\n',raw) if p.strip()]
    title=parts[0]; body=[]
    for p in parts[1:]: body+=split_para(p)
    targets=sorted(glob.glob(f'{REPO}/{n}_第*.txt'))
    assert targets,n
    for t in targets:
        name=os.path.basename(t)
        old_title=open(t,encoding='utf-8-sig').read().split('\n')[0].strip()
        tt=old_title if len(targets)>1 else title
        out='\ufeff'+tt+'\r\n\r\n'+'\r\n\r\n'.join('\u3000\u3000'+p for p in body)+'\r\n'
        open(f'{OUT}/{name}','w',encoding='utf-8',newline='').write(out)
print('done',len(os.listdir(OUT)))
