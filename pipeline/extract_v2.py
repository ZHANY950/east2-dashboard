# -*- coding: utf-8 -*-
"""东二区数据看板 V2 — 大区数据概览(新版7模块) 数据提取
数据源:
1. /tmp/tth_q3.csv          腾讯文档 1-TTH-进货/Q3月度预估 rows56-78 (TTH进度+季度预估)
2. 分DM日均tth (KvgABFRwjvJr/BB08J2) 已保存 /tmp/dm_daily.csv (本脚本内嵌解析自 stdout 抓取文件)
3. /tmp/mjq_data.csv        瞄准镜 1008行 (244客户进展)
4. /tmp/wps_244.json        WPS 2+4+4团队跟进 399行
5. 月表8.26 (本地)          5-7月实际日均 + 8月周均
6. /tmp/dzdk/word/media/    先锋图片
"""
import csv, json, base64, io, os, re as _re
from collections import defaultdict, Counter
from datetime import datetime, timedelta
import openpyxl

# ===== 路径配置（环境变量可覆盖：GitHub Actions 云端用仓库 sources/ 目录，本地默认 /tmp） =====
SRC_DIR = os.environ.get("EAST2_SRC", "/tmp")
def _p(name): return os.path.join(SRC_DIR, name)
YB_DIRS = [d for d in os.environ.get(
    "EAST2_YB_DIR",
    "/Users/zhangyun/Desktop/基础数据源" + os.pathsep + "/Users/zhangyun/Desktop/会议有效性ppt"
).split(os.pathsep) if d]
DZDK_DIR = os.environ.get("EAST2_DZDK", "/tmp/dzdk")

def _pick_latest(pattern):
    """跨目录 glob 后按文件名内日期(m.d)排序取最新（纯字符串排序在 10 月会错序：'10.1'<'8.26'）"""
    cands = []
    for d in YB_DIRS:
        cands += list(__import__("glob").glob(os.path.join(d, pattern)))
    def key(p):
        m = _re.search(r"(\d+)\.(\d+)", os.path.basename(p))
        return (int(m.group(1)), int(m.group(2))) if m else (0, 0)
    return sorted(cands, key=key)[-1] if cands else None

DMS = ["孟鈃", "郑家成", "何方禹", "李路", "张鑫", "卜先峰"]

def num(v):
    if v is None: return None
    s = str(v).replace(",", "").strip()
    if s.endswith("%"):
        try: return round(float(s[:-1]), 1)
        except: return None
    try: return float(s)
    except: return None

# ---------- 1. TTH进度 (AP9分周) rows: 59-65 (csv line idx 3-9 in saved file) ----------
rows = list(csv.reader(open(_p("tth_q3.csv"), encoding="utf-8")))
tth_progress = []
for r in rows[3:10]:
    if len(r) < 30: continue
    dm = r[4].strip()
    if not dm: continue
    t = {"dm": dm,
         "quota": num(r[5]), "target": num(r[6]), "target_rate": num(r[7]),
         "actual": num(r[8]), "actual_rate": num(r[9])}
    # 每周块起点 b：W1=11 W2=19 W3=27 W4=35 W5=43
    # 块内：折算=b, 实际折算=b+5, 实际达成(b+6 = R列)
    w = []
    for b in [11, 19, 27, 35, 43]:
        tgt = num(r[b]) if b < len(r) else None           # 目标折算
        act = num(r[b + 5]) if b + 5 < len(r) else None   # 实际折算
        rate = num(r[b + 6]) if b + 6 < len(r) else None  # 实际达成（R列）
        w.append({"tgt": tgt, "act": act, "rate": rate})
    t["weeks"] = w
    tth_progress.append(t)

# ---------- 2. 季度预估 rows 72-78 (csv line idx 16-22) ----------
quarter_est = []
for r in rows[16:23]:
    if len(r) < 16: continue
    dm = r[4].strip()
    if not dm or dm in ("DM",): continue
    def g(i): return num(r[i]) if i < len(r) else None
    if g(5) is None: continue
    quarter_est.append({
        "dm": dm,
        "ap7_quota": g(5), "ap7_act": g(6), "ap7_rate": g(7),
        "ap8_quota": g(8), "ap8_act": g(9), "ap8_rate": g(10),
        "ap9_quota": g(11), "ap9_est": g(12), "ap9_rate": g(13),
        "q3_est": g(14), "q3_rate": g(15),
    })

# ---------- 3. 分DM日均tth (sheet BB08J2) ----------
dm_daily_rows = []
# 重新从已抓取的输出解析 —— 直接内嵌(从腾讯文档已验证的数据)
DM_DAILY = {
    "孟鈃":   [154,149,161,122,117,117,132,292,147,160,177,None,None],
    "郑家成": [89,80,77,97,93,93,105,152,89,87,91,None,None],
    "何方禹": [185,189,194,159,152,153,172,270,189,181,160,None,None],
    "李路":   [141,117,108,135,130,130,147,142,111,104,102,None,None],
    "张鑫":   [147,143,139,134,129,129,145,242,140,133,131,None,None],
    "卜先峰": [22,25,30,46,45,45,50,64,30,30,32,None,None],
    "合计":   [738,702,708,694,666,667,752,1162,705,694,692,None,None],
}
DM_DAILY_KEYS = ["d5","d6","d7","q3_idx","ap7_idx","ap8_idx","ap9_idx","ap9_tgt","w1","w2","w3","w4","w5"]
dm_daily = {dm: dict(zip(DM_DAILY_KEYS, vals)) for dm, vals in DM_DAILY.items()}

# 日度数据 (8/2-8/31)
DM_DAILY_DAYS = [
    ("8/2",[16,20,32,28,36,4]),("8/3",[148,72,180,104,144,24]),("8/4",[160,85,196,112,128,28]),
    ("8/5",[112,72,188,110,136,32]),("8/6",[128,120,176,104,120,36]),("8/7",[172,76,172,96,136,24]),
    ("8/9",[20,16,32,20,28,4]),("8/10",[192,60,180,100,132,36]),("8/11",[172,90,172,104,128,28]),
    ("8/12",[116,84,164,92,120,24]),("8/13",[148,110,192,102,128,34]),("8/14",[152,76,164,100,128,24]),
    ("8/16",[28,32,32,24,20,4]),("8/17",[172,76,164,92,124,40]),("8/18",[180,104,152,93,128,28]),
    ("8/19",[156,69,160,108,132,30]),("8/20",[160,96,152,100,124,29]),("8/21",[188,76,140,92,128,28]),
    ("8/23",[24,36,40,24,20,16]),("8/24",[228,72,180,112,128,37]),("8/25",[196,84,188,104,132,40]),
    ("8/26",[140,92,188,92,120,32]),
]
daily = [{"date": d, "vals": dict(zip(DMS, v)), "total": sum(v)} for d, v in DM_DAILY_DAYS]

# ---------- 4. 月表: 5-7月实际日均 + 8月周均 ----------
WD = {"5月": 21, "6月": 22, "7月": 23}
WWD = {"8月第1周": 5, "8月第2周": 5, "8月第3周": 5, "8月第4周": 5}
# 月表：自动取 基础数据源 里最新的【月表】患者画像每日跟进*.xlsx（刷新时无需改代码；云端=仓库 sources/）
_yb = _pick_latest("【月表】患者画像每日跟进*.xlsx")
YB = _yb or "/Users/zhangyun/Desktop/基础数据源/【月表】患者画像每日跟进8.26.xlsx"
print("月表使用:", YB)
wb = openpyxl.load_workbook(YB, read_only=True, data_only=True)
ws = wb["基础数据"]
dm_month = defaultdict(lambda: defaultdict(float))
dm_week = defaultdict(lambda: defaultdict(float))
for r in ws.iter_rows(min_row=2, values_only=True):
    if r[0] is None: continue
    m, dm, wk = str(r[0]), str(r[6]) if r[6] else "", str(r[3]) if r[3] else ""
    try: v = float(r[22] or 0)
    except: continue
    if not dm: continue
    if m in WD: dm_month[dm][m] += v
    elif m == "8月" and wk in WWD: dm_week[dm][wk] += v
wb.close()
dm_actual = {}
for dm in DMS:
    dm_actual[dm] = {
        "d5": round(dm_month[dm]["5月"] / WD["5月"], 1),
        "d6": round(dm_month[dm]["6月"] / WD["6月"], 1),
        "d7": round(dm_month[dm]["7月"] / WD["7月"], 1),
        "w1": round(dm_week[dm]["8月第1周"] / 5, 1),
        "w2": round(dm_week[dm]["8月第2周"] / 5, 1),
        "w3": round(dm_week[dm]["8月第3周"] / 5, 1),
        "w4": round(dm_week[dm]["8月第4周"] / 5, 1),
    }
tot = {"d5": round(sum(dm_month[d]["5月"] for d in DMS)/21,1), "d6": round(sum(dm_month[d]["6月"] for d in DMS)/22,1),
       "d7": round(sum(dm_month[d]["7月"] for d in DMS)/23,1)}
for wk in ["8月第1周","8月第2周","8月第3周","8月第4周"]:
    tot["w"+wk[-2]] = round(sum(dm_week[d][wk] for d in DMS)/5, 1)
dm_actual["合计"] = tot

# ---------- 5. 瞄准镜 244客户进展 ----------
rows = list(csv.reader(open(_p("mjq_data.csv"), encoding="utf-8")))
# 列: 3=DM 4=专员 5=医院 7=医院标签 10=准入 12=医生 13=list 14=244标签 15=科室 16=亚专业 17=分型
# 36=观念现状(7月) 37=观念目标(8月) 38-47=2025.11-2026.8月度TTH 48-50=2026.9-11
CONCEPT_LEVEL = {"不管不治":0, "阶梯治疗":1, "止痛优选":2, "短期治痛":3, "治痛管理":4, "资深治痛管理":5, "治痛管理大师":6}
def cpt_main(text):
    if not text: return ""
    t = str(text)
    for c in ["治痛管理大师", "资深治痛管理", "治痛管理", "短期治痛", "止痛优选", "阶梯治疗", "不管不治"]:
        if c in t: return c
    return t.strip()[:10]
TIME_PCT = round(18/21*100, 1)  # 截至8/26 时间进度
cust244 = []
for r in rows:
    if len(r) < 48: continue
    dm, mics, doc = r[3].strip(), r[4].strip(), r[12].strip()
    if not doc: continue
    t244 = r[14].strip()
    if not t244 or t244 == "否": continue
    tgt_cpt = cpt_main(r[37])
    ctype = r[17].strip()
    now_cpt = cpt_main(r[36])
    # 颜色+目标TTH
    if tgt_cpt in ("治痛管理", "资深治痛管理", "治痛管理大师"):
        color, tgt_tth = "green_dk", 130
    elif tgt_cpt == "短期治痛":
        color, tgt_tth = "green_lt", 70
    elif tgt_cpt == "止痛优选" and ctype == "C":
        color, tgt_tth = "blue", 30
    else:
        color, tgt_tth = "gray", None
    tth8 = num(r[46]) or 0  # 2026年8月 (col 46 = 38+8)
    tth7 = num(r[45]) or 0
    cust244.append({
        "dm": dm, "mics": mics, "hosp": r[5].strip(), "tag": r[7].strip(),
        "doc": doc, "sub": r[16].strip(), "ctype": ctype,
        "cpt_now": now_cpt, "cpt_tgt": tgt_cpt,
        "color": color, "tgt": tgt_tth,
        "tth7": tth7, "tth8": tth8,
        "rate": round(tth8/tgt_tth*100, 1) if tgt_tth else None,
    })
# 汇总
def agg_c244(items):
    g = {"green_dk": 0, "green_lt": 0, "blue": 0, "gray": 0}
    for c in items: g[c["color"]] += 1
    ok = sum(1 for c in items if c["tgt"] and c["tth8"] >= c["tgt"])
    warn = sum(1 for c in items if c["tgt"] and c["rate"] is not None and c["rate"] < TIME_PCT*0.7)
    tth8 = round(sum(c["tth8"] for c in items), 0)
    tth7 = round(sum(c["tth7"] for c in items), 0)
    return {"n": len(items), "green_dk": g["green_dk"], "green_lt": g["green_lt"],
            "blue": g["blue"], "gray": g["gray"], "ok": ok, "warn": warn, "tth7": tth8 if False else tth7, "tth8": tth8}
c244_by_dm = {dm: agg_c244([c for c in cust244 if c["dm"] == dm]) for dm in set(c["dm"] for c in cust244)}
c244_total = agg_c244(cust244)

# ---------- 5.5 瞄准镜 全量客户进展（新模块⑧） ----------
# 区域规则阈值：月纯销 → 层级 → 观念名称
def concept_of(tth):
    t = tth or 0
    if t <= 0:  return ("不管不治", 0)
    if t < 30:  return ("阶梯治疗", 1)
    if t < 70:  return ("止痛优选", 2)
    if t < 130: return ("短期治痛", 3)
    if t < 300: return ("治痛管理", 4)
    if t < 500: return ("资深治痛管理", 5)
    return ("治痛管理大师", 6)

# 目标观念 → 目标TTH（取该层级下限）
TGT_TTH = {"治痛管理大师": 500, "资深治痛管理": 300, "治痛管理": 130,
           "短期治痛": 70, "止痛优选": 30, "阶梯治疗": 1, "不管不治": 0}

# 月度TTH列: 38-47 = 2025.11 - 2026.8（共10个月）
M8_MONTHS = ["2025.11", "2025.12", "2026.1", "2026.2", "2026.3",
             "2026.4", "2026.5", "2026.6", "2026.7", "2026.8"]
M8_CONCEPTS = ["不管不治", "阶梯治疗", "止痛优选", "短期治痛",
               "治痛管理", "资深治痛管理", "治痛管理大师"]

cust_progress = []
for r in rows:
    if len(r) < 48: continue
    doc = r[12].strip()
    if not doc: continue
    tths = [num(r[i]) or 0 for i in range(38, 48)]        # 逐月纯销
    lvs = [concept_of(t)[1] for t in tths]                # 逐月观念层级0-6
    cust_progress.append({
        "dm": r[3].strip(), "mics": r[4].strip(), "hosp": r[5].strip(),
        "doc": doc, "sub": r[16].strip(), "ctype": r[17].strip(),
        "tgt_cpt": cpt_main(r[37]),
        "tths": tths, "lvs": lvs,
    })
cust_progress.sort(key=lambda x: (x["dm"], x["hosp"], x["doc"]))
subs = sorted(set(c["sub"] for c in cust_progress if c["sub"]))
ctypes = sorted(set(c["ctype"] for c in cust_progress if c["ctype"]))

# ---------- 6. WPS 2+4+4 团队跟进 ----------
wps = json.load(open(_p("wps_244.json"), encoding="utf-8"))
team_summary = {}
for dm in set(x["dm"] for x in wps):
    items = [x for x in wps if x["dm"] == dm]
    tgt = sum(x["target"] or 0 for x in items)
    est = sum(x["month_est"] or 0 for x in items)
    act = sum((x["w1"] or 0)+(x["w2"] or 0)+(x["w3"] or 0)+(x["w4"] or 0) for x in items)
    # 观念计数
    cpt = Counter(x["concept"] for x in items)
    team_summary[dm] = {
        "n": len(items), "mics_n": len(set(x["mics"] for x in items)),
        "target": round(tgt, 0), "est": round(est, 0), "act": round(act, 0),
        "rate": round(est/tgt*100, 1) if tgt else None,  # 当月纯销预估÷目标
        "cpt": dict(cpt),
        "gd": sum(x["gd"] or 0 for x in items), "lb": sum(x["lb"] or 0 for x in items),
        "sf": sum(x["sf"] or 0 for x in items), "pim": sum(x["pimcall"] or 0 for x in items),
    }

# ---------- 7. 303 项目 ----------
def build_p303():
    import subprocess, sys
    py = os.environ.get("EAST2_PY", "/Users/zhangyun/.workbuddy/binaries/python/versions/3.13.12/bin/python3")
    base = os.environ.get("EAST2_TD_DIR", "/Users/zhangyun/.workbuddy/plugins/cache/workbuddy-builtin/tencent-docs-plugin/1.0.0/skills/tencent-docs")

    # 1) 取数据和样式（如已存在则复用；云端 Actions 无腾讯文档票据，必须由 sources/ 提供缓存文件）
    def call(args):
        out = subprocess.check_output(args, stderr=subprocess.DEVNULL, timeout=30, cwd=base)
        return json.loads(out)

    if not os.path.exists(_p("p303_raw.csv")):
        raw = call([py, "tencentdocs.py", "tdoc_call", "sheet-mcp", "get_cell_data",
                    json.dumps({"file_id": "KvgABFRwjvJr", "sheet_id": "qbjnqg",
                                "start_row": 0, "start_col": 0, "end_row": 79, "end_col": 35,
                                "return_csv": True})])
        text = json.loads(raw["result"]["content"][0]["text"])["csv_data"]
        open(_p("p303_raw.csv"), "w", encoding="utf-8").write(text)
    if not os.path.exists(_p("p303_style.json")):
        raw = call([py, "tencentdocs.py", "tdoc_call", "sheet-mcp", "get_cell_style",
                    json.dumps({"file_id": "KvgABFRwjvJr", "sheet_id": "qbjnqg",
                                "start_row": 0, "start_col": 0, "end_row": 79, "end_col": 30})])
        open(_p("p303_style.json"), "w", encoding="utf-8").write(json.dumps(raw, ensure_ascii=False))

    csv_text = open(_p("p303_raw.csv"), encoding="utf-8").read()
    csv.field_size_limit(10000000)
    rows = list(csv.reader(io.StringIO(csv_text)))
    style_raw = json.load(open(_p("p303_style.json"), encoding="utf-8"))
    style_cells = json.loads(style_raw["result"]["content"][0]["text"])["cells"]

    # 样式映射
    def norm_color(c):
        if not c: return None
        return "#" + (c[2:] if c.startswith("FF") else c).upper()

    styles = {}
    for c in style_cells:
        bg = norm_color(c.get("background_color", ""))
        fg = norm_color(c.get("font_color", ""))
        bold = c.get("bold", False)
        # 字体颜色：深背景用白字；无背景时不强变白字（避免看不清）
        if bg and not fg:
            rgb = tuple(int(bg[i:i+2], 16) for i in (1, 3, 5))
            r, g, b = rgb
            if r > 180 and g > 180 and b < 140:        # 黄底 → 黑字（高亮底）
                fg = "#000000"
            elif g > 100 or rgb[0] > 200 or (rgb[0] > 150 and g > 100):  # 绿/橙 深底白字
                fg = "#FFFFFF"
        if not bg and fg == "#FFFFFF":
            fg = None
        styles[(c["row"], c["col"])] = {"bg": bg, "fg": fg, "bold": bold}

    def cell(r, c):
        v = rows[r][c] if r < len(rows) and c < len(rows[r]) else ""
        # 清理空字符
        v = "".join(ch for ch in v if ord(ch) >= 32 or ch in "\n\t")
        return {"v": v.strip(), **styles.get((r, c), {})}

    def make_table(ranges, headers=None):
        """按给定的 (row_start, row_end, col_list) 抽一个表"""
        out = []
        for r0, r1, cols in ranges:
            for r in range(r0, min(r1, len(rows))):
                row = []
                for c in cols:
                    row.append(cell(r, c))
                out.append(row)
        return out

    # 员工维度：8月第二周(cols0-3) / 第三周(cols5-8)
    emp_w2 = make_table([
        (0, 1, [0]),      # 大标题
        (1, 2, [0]),      # 周标题
        (2, 5, [0, 1, 2, 3]),   # 0产出
        (5, 12, [0, 1, 2, 3]),  # 0 3M产出
        (13, 38, [0, 1, 2, 3]), # 橙标
        (39, 56, [0, 1, 2, 3]), # 绿标
    ])
    emp_w3 = make_table([
        (1, 2, [5]),      # 周标题（不要重复大标题）
        (2, 5, [5, 6, 7, 8]),   # 0产出
        (5, 12, [5, 6, 7, 8]),  # 0 3M产出
        (13, 38, [5, 6, 7, 8]), # 橙标
        (39, 56, [5, 6, 7, 8]), # 绿标
    ])

    # 客户维度：
    # 第二周汇总 col10,11,14,18；名单1:10-12, 名单2:14-16, 名单3:18-20
    # 第三周汇总 col22,23,26,30；名单1:22-24, 名单2:26-28, 名单3:30-32
    def cust_week(summary_cols, list_cols, summary_start=0):
        summary = make_table([(summary_start, 10, summary_cols)])
        lists = [
            {"rows": make_table([(11, 60, list_cols[0])])},
            {"rows": make_table([(11, 60, list_cols[1])])},
            {"rows": make_table([(11, 60, list_cols[2])])},
        ]
        return {"summary": summary, "lists": lists}

    cust_w2 = cust_week([10, 11, 14, 18], [[10, 11, 12], [14, 15, 16], [18, 19, 20]], 0)
    cust_w3 = cust_week([22, 23, 26, 30], [[22, 23, 24], [26, 27, 28], [30, 31, 32]], 1)

    return {
        "emp": {
            "week2": {"title": "8月第二周", "rows": emp_w2},
            "week3": {"title": "8月第三周", "rows": emp_w3},
        },
        "cust": {
            "week2": {"title": "第二周", **cust_w2},
            "week3": {"title": "第三周", **cust_w3},
        }
    }

p303 = build_p303()

# ---------- 8. 先锋图片 (压缩) ----------
pio = []
try:
    from PIL import Image
    for idx, cap in [(4, "TTH日预估周增长先锋"), (5, "治痛周先锋")]:
        p = os.path.join(DZDK_DIR, "word", "media", f"image{idx}.png")
        if not os.path.exists(p): continue
        im = Image.open(p).convert("RGB")
        w, h = im.size
        if w > 900:
            im = im.resize((900, int(h*900/w)), Image.LANCZOS)
        buf = io.BytesIO()
        im.save(buf, "JPEG", quality=72)
        b64 = base64.b64encode(buf.getvalue()).decode()
        pio.append({"cap": cap, "img": "data:image/jpeg;base64," + b64})
        print(f"先锋图{idx}: {len(buf.getvalue())//1024}KB")
except ImportError:
    print("PIL不可用，先锋图跳过")

# ---------- 8. TTH预估目标 & TTH预估——周均 (腾讯文档 分DM日均tth A12:R49) ----------
def build_tth_weekly():
    rows1 = list(csv.reader(open(_p("dm_daily_part1.csv"), encoding="utf-8")))
    tth_target = {"headers": rows1[0][:14], "rows": [r[:14] for r in rows1[1:8]]}

    rows2 = list(csv.reader(open(_p("dm_daily_part2.csv"), encoding="utf-8")))
    # 合并左（8月）右（6-7月）两块日期数据，日期冲突时取非空值
    all_data = {}
    for r in rows2:
        # left block
        if len(r) > 0 and r[0] and "/" in r[0]:
            try:
                d = datetime.strptime(r[0], "%Y/%m/%d")
                vals = [float(x) if x.strip() else None for x in r[1:8]]
                all_data[d] = vals
            except Exception:
                pass
        # right block
        if len(r) > 10 and r[10] and "/" in r[10]:
            try:
                d = datetime.strptime(r[10], "%Y/%m/%d")
                vals = [float(x) if x.strip() else None for x in r[11:18]]
                if d in all_data:
                    existing = all_data[d]
                    vals = [vals[i] if vals[i] is not None else existing[i] for i in range(7)]
                all_data[d] = vals
            except Exception:
                pass

    ALL_DMS = DMS + ["大区总计"]

    # 窗口终点 = 数据源中有实际数值（非空且非0）的最大日期；起点 = 终点 - 30 天
    valid_dates = [d for d, vals in all_data.items() if any(v is not None and v != 0 for v in vals)]
    if not valid_dates:
        end = datetime(2026, 8, 26)
    else:
        end = max(valid_dates)
    start = end - timedelta(days=30)

    # 1) 读全量原始序列（含周末）
    raw_dates = []
    d = start
    while d <= end:
        raw_dates.append(d)
        d += timedelta(days=1)

    raw = {}
    for i, dm in enumerate(ALL_DMS):
        vals = []
        for dd in raw_dates:
            v = all_data.get(dd, [None] * 7)[i]
            vals.append(v)
        raw[dm] = vals

    # 2) 周末 TTH 加到下周一（如果周一在范围内）
    rolled = {dm: [None] * len(raw_dates) for dm in ALL_DMS}
    for dm in ALL_DMS:
        for idx, dd in enumerate(raw_dates):
            v = raw[dm][idx]
            if v is None:
                continue
            if dd.weekday() >= 5:  # 周六/周日
                days_to_mon = 7 - dd.weekday()
                mon = dd + timedelta(days=days_to_mon)
                if mon in raw_dates:
                    midx = raw_dates.index(mon)
                    rolled[dm][midx] = (rolled[dm][midx] or 0) + v
            else:
                rolled[dm][idx] = (rolled[dm][idx] or 0) + v

    # 3) 显示序列：仅工作日
    dates, labels = [], []
    for idx, dd in enumerate(raw_dates):
        if dd.weekday() < 5:
            dates.append(dd)
            labels.append(dd.strftime("%m/%d"))

    series = {dm: [rolled[dm][raw_dates.index(dd)] for dd in dates] for dm in ALL_DMS}

    # 4) 周均：每周五回望周一至周五（周一已含周末归并），有几天算几天
    # 包含窗口后第一个周五，使末尾不完整周也能在对应周一显示柱子
    first_fri = start + timedelta(days=(4 - start.weekday()) % 7)
    last_fri = end + timedelta(days=(4 - end.weekday()) % 7)
    fridays = []
    dd = first_fri
    while dd <= last_fri:
        fridays.append(dd)
        dd += timedelta(days=7)

    weekly = {}
    for dm in ALL_DMS:
        wv = []
        for fri in fridays:
            s, n = 0, 0
            for offset in [4, 3, 2, 1, 0]:
                wd = fri - timedelta(days=offset)
                if wd in dates:
                    idx = dates.index(wd)
                    v = series[dm][idx]
                    if v is not None:
                        s += v; n += 1
            wv.append(round(s / n, 1) if n else None)
        weekly[dm] = wv

    # 5) 周均柱状位置在每周五（周均=周一至周五平均，周末已并入下周一）
    fridays_pos = fridays

    def linreg(xs, ys):
        n = len(xs); xm, ym = sum(xs) / n, sum(ys) / n
        num = sum((xs[i] - xm) * (ys[i] - ym) for i in range(n))
        den = sum((xs[i] - xm) ** 2 for i in range(n))
        if den == 0: return [ym] * n
        b = num / den; a = ym - b * xm
        return [round(a + b * xs[i], 1) for i in range(n)]

    trend_daily, trend_weekly, trend_weekly_full = {}, {}, {}
    for dm in ALL_DMS:
        xs = list(range(len(dates)))
        trend_daily[dm] = linreg(xs, [v if v is not None else 0 for v in series[dm]])
        wxs = list(range(len(fridays)))
        # linreg 要求 ys 长度与 xs 一致；weekly[dm] 可能含 None，用 0 填充
        trend_weekly[dm] = linreg(wxs, [v if v is not None else 0 for v in weekly[dm]])
        tw = trend_weekly[dm]
        b = (tw[-1] - tw[0]) / (len(tw) - 1) if len(tw) > 1 else 0
        a = tw[0]
        trend_weekly_full[dm] = [round(a + b * (i / 5), 1) for i in range(len(dates))]

    tth_weekly = {
        "labels": labels, "dm_list": ALL_DMS, "daily": series, "weekly": weekly,
        "weekly_labels": [d.strftime("%m/%d") for d in fridays],
        "fridays": [d.strftime("%m/%d") for d in fridays_pos],
        "trend_daily": trend_daily, "trend_weekly": trend_weekly,
        "trend_weekly_full": trend_weekly_full,
        "window": {"start": start.strftime("%m/%d"), "end": end.strftime("%m/%d")}
    }
    return tth_target, tth_weekly

tth_target, tth_weekly = build_tth_weekly()

# ---------- 8.1 同步源表绿字单元格到 tth_target ----------
def fetch_green_mask():
    import subprocess
    py = "/Users/zhangyun/.workbuddy/binaries/python/versions/3.13.12/bin/python3"
    cmd = [
        py, "tencentdocs.py", "tdoc_call", "sheet-mcp", "get_cell_style",
        json.dumps({"file_id": "KvgABFRwjvJr", "sheet_id": "BB08J2",
                    "start_row": 0, "start_col": 0, "end_row": 7, "end_col": 13})
    ]
    try:
        out = subprocess.check_output(cmd, stderr=subprocess.DEVNULL, timeout=30,
                                      cwd="/Users/zhangyun/.workbuddy/plugins/cache/workbuddy-builtin/tencent-docs-plugin/1.0.0/skills/tencent-docs")
        cells = json.loads(json.loads(out)["result"]["content"][0]["text"])["cells"]
    except Exception as e:
        print("绿字同步失败:", e)
        return []
    def parse(c):
        if not c: return None
        h = c[2:] if c.startswith("FF") else c
        return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))
    green = []
    for cc in cells:
        f = cc.get("font_color", "")
        if not f: continue
        rgb = parse(f)
        if rgb and rgb[1] > rgb[0] + 20 and rgb[1] > rgb[2] + 20:
            green.append([cc["row"], cc["col"], "#" + f[2:].upper()])
    return green

tth_target["green"] = fetch_green_mask()

# ---------- 输出 ----------
data = json.load(open(_p("dashboard_data.json"), encoding="utf-8"))
data["v2"] = {
    "time_pct": TIME_PCT,
    "tth_progress": tth_progress,
    "quarter_est": quarter_est,
    "dm_daily": dm_daily,
    "dm_daily_days": daily,
    "dm_actual": dm_actual,
    "cust244": cust244,
    "c244_by_dm": c244_by_dm,
    "c244_total": c244_total,
    "team": wps,
    "team_summary": team_summary,
    "p303": p303,
    "pio": pio,
    "tth_target": tth_target,
    "tth_weekly": tth_weekly,
    "cust_progress": cust_progress,
    "subs": subs,
    "ctypes": ctypes,
    "m8_months": M8_MONTHS,
    "m8_concepts": M8_CONCEPTS,
}
json.dump(data, open(_p("dashboard_data2.json"), "w", encoding="utf-8"), ensure_ascii=False)
print("\n=== 汇总校验 ===")
print("TTH进度:", [(t["dm"], t["actual"], t["actual_rate"]) for t in tth_progress])
print("季度预估:", [(q["dm"], q["q3_est"], q["q3_rate"]) for q in quarter_est])
print("244客户:", c244_total, " 分DM:", {k: v["n"] for k, v in c244_by_dm.items()})
print("团队汇总:", {k: (v["n"], v["rate"]) for k, v in team_summary.items()})
print("月表实际日均:", dm_actual["合计"])
print("文件大小:", os.path.getsize(_p("dashboard_data2.json"))//1024, "KB")
