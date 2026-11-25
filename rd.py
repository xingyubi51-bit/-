import sys,glob,re
a,b=int(sys.argv[1]),int(sys.argv[2])
for n in range(a,b+1):
    fs=sorted(glob.glob(f'/tmp/src_repo/{n}_第*.txt'))
    for f in fs:
        t=open(f,encoding='utf-8-sig').read().replace('\r','')
        t=re.sub(r'\n\s*\n','\n',t).replace('\u3000','')
        print(f'@@{n}');print(t.strip());print()
