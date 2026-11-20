#!/usr/bin/env python3
"""长段拆分：把超过阈值的段落，在句末（不在引号内）拆成两段或多段，每段不少于40字。
用法：python3 tools/split_long.py draft [阈值=260]"""
import glob, os, sys

def split_points(p):
    pts, depth = [], 0
    for i, ch in enumerate(p):
        if ch == '“': depth += 1
        elif ch == '”': depth = max(0, depth - 1)
        if depth == 0 and ch == '。' and i + 1 < len(p):
            pts.append(i + 1)
        elif depth == 0 and ch == '”' and i > 0 and p[i-1] in '。！？' and i + 1 < len(p):
            pts.append(i + 1)
    return sorted(set(pts))

def split(p, limit):
    if len(p) <= limit:
        return [p]
    pts = [x for x in split_points(p) if 40 <= x <= len(p) - 40]
    if not pts:
        return [p]
    mid = len(p) / 2
    cut = min(pts, key=lambda x: abs(x - mid))
    return split(p[:cut], limit) + split(p[cut:], limit)

if __name__ == '__main__':
    src = sys.argv[1]
    limit = int(sys.argv[2]) if len(sys.argv) > 2 else 260
    for f in sorted(glob.glob(os.path.join(src, '*.txt'))):
        lines = [l.strip() for l in open(f, encoding='utf-8').read().split('\n') if l.strip()]
        out = [lines[0]]
        for p in lines[1:]:
            out += split(p, limit)
        open(f, 'w', encoding='utf-8').write('\n'.join(out) + '\n')
        print(os.path.basename(f), len(lines) - 1, '->', len(out) - 1)
