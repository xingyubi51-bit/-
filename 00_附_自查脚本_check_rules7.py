#!/usr/bin/env python3
"""第七轮规范自查脚本：句式克制 + 分段节奏。
用法：python3 check_rules7.py 章节1.txt 章节2.txt ...   （或传入目录）
检查项：
  1. 段均字数在 20—60 之间（不含标题行）
  2. 95 字及以上的段落数必须为 0；80 字以上的段落尽量少
  3. 不足 10 字的单行段数量（提示用）
  4. “不是……，是……”及变体命中数（每几章合计最多一两处）
注意：本脚本只用来“检查”。分段必须人工逐章通读完成，不得用脚本批量分段。
"""
import glob, os, re, sys

CONTRAST = [
    re.compile(r'不是[^。！？“”\n]{0,40}[，,；—]+\s*(而)?是'),
    re.compile(r'并非[^。！？“”\n]{0,40}[，,；—]+\s*(而)?是'),
    re.compile(r'哪里是[^。！？“”\n]{0,40}[，,；—]+\s*分明是'),
]


def paras(text):
    lines = [l.strip().replace('\u3000', '').strip() for l in text.replace('\r', '').split('\n')]
    lines = [l for l in lines if l]
    return lines[0], lines[1:]


def check(path):
    text = open(path, encoding='utf-8-sig').read()
    title, p = paras(text)
    n = len(p)
    chars = sum(len(x) for x in p)
    avg = chars / n
    over95 = [x for x in p if len(x) >= 95]
    over80 = sum(1 for x in p if len(x) > 80)
    under10 = sum(1 for x in p if len(x) < 10)
    body = '\n'.join(p)
    hits = sum(len(c.findall(body)) for c in CONTRAST)
    ok = 20 <= avg <= 60 and not over95
    print(f"{'OK  ' if ok else 'FAIL'} {os.path.basename(path)[:24]:26s} 段={n:3d} 字={chars:5d} 段均={avg:5.1f} "
          f">=95:{len(over95)} >80:{over80} <10:{under10} 不是…是:{hits}")
    for x in over95:
        print('      ↳ 过长段：', x[:40], '…')
    return ok, hits


def main(args):
    files = []
    for a in args or ['.']:
        if os.path.isdir(a):
            files += sorted(glob.glob(os.path.join(a, '*_第*章*.txt')))
        else:
            files.append(a)
    total_hits = 0
    bad = 0
    for f in files:
        ok, hits = check(f)
        total_hits += hits
        bad += 0 if ok else 1
    print(f"\n共 {len(files)} 章；不合格 {bad} 章；“不是……，是……”合计 {total_hits} 处（建议每几章不超过 1—2 处）")


if __name__ == '__main__':
    main(sys.argv[1:])
