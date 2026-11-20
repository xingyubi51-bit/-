#!/usr/bin/env python3
"""写作规范自查脚本：每写完一章必须跑一遍。
用法：python3 tools/check_novel.py [目录或文件 ...]   （默认检查 novel_src/）
检查项：
  1. 段均字数 >= 30（不含标题行）
  2. 20 字以内的短段占比（建议 < 25%）
  3. 一二三式排比 / 序数罗列（命中即不合格）
  4. 神态描写密度（每千字至少 6 处神态词）
  5. 擦边词统计（新增）：每十章至少 4 章含擦边描写，其中至少 1 章为福利章
  6. 亲密章配额（新增）：每三十章至少 1 个亲密章
  7. 过露词拦截（新增）：出现器官、过程类直白词汇，判 FAIL
"""
import glob, os, re, sys

ENUM_PATTERNS = [
    r'第[一二三四五六七八九十]+[，,、：:]',      # 第一…第二…
    r'[其]?[一二三四五六]是[，,：:]',            # 一是…二是…
    r'其[一二三四五六][，,：:、]',               # 其一…其二…
    r'[一二三四五六]来[，,：:]',                 # 一来…二来…
    r'[一二三四五六]则[，,：:]',
    r'[首其再]先[，,]|其次[，,]|再次[，,]',
    r'[一二三四五六七八九十]、',                 # 一、二、三、
    r'[一二三]\S{1,2}[，,]两\S{1,2}[，,]三\S{1,2}', # 一盏，两盏，三盏
    r'一\S{1,2}[，,]二\S{1,2}[，,]三\S{1,2}',
    r'[①②③④⑤⑥]|\(\d\)|（\d）|^\d[\.、]',
]
FACE_WORDS = ['眉', '目光', '眼神', '眼底', '眼角', '眼睫', '眼眶', '眸', '嘴角', '唇', '神色', '神情', '脸色',
              '面色', '脸上', '笑意', '笑了', '苦笑', '冷笑', '微笑', '皱', '瞳', '喉结', '咬着', '抿',
              '垂下眼', '抬起眼', '低下头', '偏过头', '侧过脸', '怔', '愣', '红了', '白了', '发白', '泛红',
              '肩头', '指尖', '攥', '颤']

# 擦边词：姿态、春光、特征、撞见、亲密（仅作统计，不用于判错）
SENSE_WORDS = ['锁骨', '肩头', '颈侧', '腰线', '腰身', '衣襟', '领口', '中衣', '湿透', '贴着', '赤足', '足踝',
               '小腿', '发梢', '薄汗', '耳根', '耳尖', '春光', '雪白', '半透', '衣带', '裙摆', '抚过', '吻',
               '相拥', '同榻', '肌肤', '体温', '撞见', '背过身', '朱砂', '红痕', '纱衫', '滑落']
# 亲密章标志词：命中三个及以上，视为亲密章
INTIMATE_WORDS = ['同榻', '肌肤相亲', '烛火应声而灭', '吹灯', '帐幔', '衣衫散乱', '枕边', '榻上', '相拥而眠',
                  '红痕', '纱衫', '落在脚边', '晨光', '银铃']
# 过露词：出现即 FAIL（本书只写软色情，不写器官与过程）
EXPLICIT_BANNED = ['私处', '下体', '乳尖', '抽插', '交合', '体液', '精液']

SENSE_MIN = 4       # 一章中擦边词不少于此数，算“含擦边”
WELFARE_MIN = 10    # 一章中擦边词不少于此数，算“福利章”
INTIMATE_MIN = 3    # 亲密标志词不少于此数，算“亲密章”

SENSE_BY_NO = {}
INTIMATE_BY_NO = {}

def chapter_no(path):
    m = re.match(r'(\d+)_', os.path.basename(path))
    return int(m.group(1)) if m else None

def para_list(text):
    lines = [l.strip() for l in text.replace('\r', '').split('\n') if l.strip()]
    return lines[1:] if lines else []

def check(path):
    text = open(path, encoding='utf-8-sig').read()
    paras = para_list(text)
    if not paras:
        return None
    n = len(paras)
    chars = sum(len(p) for p in paras)
    avg = chars / n
    short = sum(1 for p in paras if len(p) < 20)
    face = sum(sum(p.count(w) for w in FACE_WORDS) for p in paras)
    face_k = face / (chars / 1000)
    enum_hits = []
    for p in paras:
        for pat in ENUM_PATTERNS:
            m = re.search(pat, p, re.M)
            if m:
                enum_hits.append(p[max(0, m.start() - 6): m.end() + 10])
                break
    sense = sum(sum(p.count(w) for w in SENSE_WORDS) for p in paras)
    intimate = sum(sum(p.count(w) for w in INTIMATE_WORDS) for p in paras)
    explicit = [w for w in EXPLICIT_BANNED if w in text]
    no = chapter_no(path)
    if no is not None:
        SENSE_BY_NO[no] = sense
        INTIMATE_BY_NO[no] = intimate
    ok = avg >= 30 and not enum_hits and face_k >= 6 and not explicit
    print(f"{'OK  ' if ok else 'FAIL'} {os.path.basename(path)[:22]:24s} 段数={n:3d} 字数={chars:5d} 段均={avg:5.1f} 短段={short/n*100:4.0f}% 神态/千字={face_k:4.1f} 排比命中={len(enum_hits)} 擦边词={sense:3d}")
    for h in enum_hits[:6]:
        print('      ↳ 排比/罗列疑似：', h)
    if explicit:
        print('      ↳ 过露词（必须删改）：', '、'.join(explicit))
    return ok

def block_report():
    if not SENSE_BY_NO:
        return
    nos = sorted(SENSE_BY_NO)
    lo, hi = nos[0], nos[-1]
    print('\n【配额提示】（只统计已检查到的整十章／整三十章区间；缺章时仅供参考）')
    warn = 0
    start = (lo - 1) // 10 * 10 + 1
    while start <= hi:
        end = start + 9
        got = [n for n in nos if start <= n <= end]
        flagged = [n for n in got if SENSE_BY_NO[n] >= SENSE_MIN]
        welfare = [n for n in got if SENSE_BY_NO[n] >= WELFARE_MIN]
        full = len(got) >= 10
        bad = full and (len(flagged) < 4 or len(welfare) < 1)
        tag = 'WARN' if bad else 'ok  '
        warn += 1 if bad else 0
        print(f"{tag} 第{start}—{end}章：含擦边 {len(flagged)} 章（需≥4），福利章 {len(welfare)} 章（需≥1），已检查 {len(got)} 章")
        start += 10
    start = (lo - 1) // 30 * 30 + 1
    while start <= hi:
        end = start + 29
        got = [n for n in nos if start <= n <= end]
        intimate = [n for n in got if INTIMATE_BY_NO[n] >= INTIMATE_MIN]
        full = len(got) >= 30
        bad = full and len(intimate) < 1
        tag = 'WARN' if bad else 'ok  '
        warn += 1 if bad else 0
        print(f"{tag} 第{start}—{end}章：亲密章 {len(intimate)} 个（需≥1），已检查 {len(got)} 章")
        start += 30
    if warn:
        print(f'配额未达标 {warn} 处：请按《创作规范与文风》第六节补写，并同步更新《伏笔表》“亲密线记录”。')

def main():
    targets = sys.argv[1:] or [os.path.join(os.path.dirname(__file__), '..', 'novel_src')]
    files = []
    for t in targets:
        if os.path.isdir(t):
            files += sorted(glob.glob(os.path.join(t, '*第*章*.txt')))
        else:
            files.append(t)
    bad = [f for f in files if check(f) is False]
    block_report()
    print('\n全部通过' if not bad else f'\n未通过 {len(bad)} 章')

if __name__ == '__main__':
    main()
