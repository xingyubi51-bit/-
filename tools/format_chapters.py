#!/usr/bin/env python3
"""把 draft/*.txt 排成仓库格式：UTF-8 BOM、CRLF、段首两个全角空格、段间空一行。"""
import glob, os, re, sys
src = sys.argv[1]; dst = sys.argv[2]
os.makedirs(dst, exist_ok=True)
for f in sorted(glob.glob(os.path.join(src, '*.txt'))):
    no = os.path.basename(f).split('.')[0]
    lines = [l.strip() for l in open(f, encoding='utf-8').read().split('\n') if l.strip()]
    title, paras = lines[0], lines[1:]
    body = '\r\n\r\n'.join('\u3000\u3000' + p for p in paras)
    text = title + '\r\n\r\n' + body + '\r\n'
    name = f"{no}_{title.replace(' ', '_')}.txt"
    with open(os.path.join(dst, name), 'w', encoding='utf-8-sig', newline='') as o:
        o.write(text)
    print(name)
