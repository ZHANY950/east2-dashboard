# -*- coding: utf-8 -*-
"""构建新版大区数据概览（v2）：替换 dashboard.html 的 region 模块，注入 dashboard_data2.json"""
import json, re, io, sys, os

# ===== 路径配置（环境变量可覆盖：云端 Actions 用仓库内路径） =====
SRC = os.environ.get("EAST2_TMPL", "/Users/zhangyun/Desktop/workbuddy/2026-08-26-18-32-05/dashboard.html")
OUT = os.environ.get("EAST2_OUT", "/Users/zhangyun/Desktop/项目汇总/workbuddy/东二区数据看板.html")
DATA = os.path.join(os.environ.get("EAST2_SRC", "/tmp"), "dashboard_data2.json")

html = io.open(SRC, encoding="utf-8").read()
data = json.load(open(DATA))

# 构建时间 = 最后刷新时间（注入 D.refreshed_at，页头按钮旁显示）
from datetime import datetime as _dt
REFRESHED_AT = _dt.now().strftime("%Y-%m-%d %H:%M")
data["refreshed_at"] = REFRESHED_AT

# ---------- 1) 标题 & 侧栏脚注 ----------
html = html.replace("<title>东二区数据看板（初版）</title>", "<title>东二区数据看板</title>")
html = html.replace(
    '数据截至：2026-08-21 底表<br>初版 v0.1 · 数据源只读分析',
    '数据截至：2026-08-26 · 最后刷新 ' + REFRESHED_AT + '<br>v2.9 · 一键刷新数据 · 数据源只读分析')

# ---------- 1.5) 加载 chartjs-plugin-datalabels ----------
html = html.replace(
    '<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js"></script>',
    '<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js"></script>\n<script src="https://cdn.jsdelivr.net/npm/chartjs-plugin-datalabels@2.2.0"></script>')

# ---------- 0.5) 收起后悬浮展开按钮 ----------
html = html.replace(
    '<div class="layout" id="layout">',
    '<div class="layout" id="layout">\n  <button class="sidebar-fab" id="sbExpand" onclick="toggleSidebar()" title="展开侧边栏">▶</button>')

# ---------- 2) CSS 追加 ----------
CSS_ADD = """/* ===== v2 颜色pill ===== */
.c-subtitle{font-size:12.5px;font-weight:600;color:var(--ink);margin:0 0 4px 2px}
.pill-c{display:inline-block;padding:1px 8px;border-radius:10px;font-size:10.5px;font-weight:600;white-space:nowrap}
.pill-gdk{background:#2e7d32;color:#fff}
.pill-glt{background:#a5d6a7;color:#1b5e20}
.pill-blue{background:#1f5fbf;color:#fff}
.pill-gray2{background:#e3e8ef;color:#5b6b7c}
/* ===== v2 先锋图 ===== */
.pio-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:12px}
.pio-card{border:1px solid var(--line);border-radius:8px;overflow:hidden;background:#fff}
.pio-card img{width:100%;display:block}
.pio-card .pio-cap{display:flex;justify-content:space-between;align-items:center;padding:6px 10px;font-size:12px;color:var(--ink2);border-top:1px solid var(--line)}
.pio-card .pio-del{color:var(--down);cursor:pointer;font-size:11px}
.pio-card .pio-del:hover{text-decoration:underline}
/* ===== v2 模块导览 ===== */
.mod-nav{display:flex;flex-wrap:wrap;gap:8px;align-items:center;background:var(--card);border:1px solid var(--line);border-radius:var(--radius);padding:10px 14px;margin-bottom:14px;box-shadow:var(--shadow)}
.mod-nav .nav-tip{font-size:12.5px;color:var(--ink2);font-weight:600;margin-right:2px}
.mod-btn{height:32px;padding:0 14px;border:1px solid var(--line);border-radius:16px;background:#fff;font-size:12.5px;color:var(--ink);cursor:pointer;transition:all .15s;white-space:nowrap}
.mod-btn:hover{border-color:var(--brand2);color:var(--brand2)}
.mod-btn.on{background:var(--brand2);border-color:var(--brand2);color:#fff;font-weight:600}
.mod-btn.collapse{color:var(--down)}
.mod-btn.collapse:hover{border-color:var(--down)}
.mod-empty{padding:64px 20px;text-align:center;color:var(--ink2);font-size:13px;border:1px dashed var(--line);border-radius:var(--radius);background:var(--card)}
.mod-empty .big{font-size:32px;margin-bottom:10px}
/* ===== v2 冻结首列(DM) ===== */
table.freeze-dm{position:relative}
table.freeze-dm th:first-child,table.freeze-dm td:first-child{position:sticky;left:0;z-index:2;min-width:92px}
table.freeze-dm thead th:first-child{background:#f3f6fb;z-index:3}
table.freeze-dm tbody td:first-child{background:#fff}
table.freeze-dm tbody tr.hi{background:#f7faff;font-weight:700}
table.freeze-dm tbody tr.hi td:first-child{background:#f7faff}
table.freeze-dm th:first-child,table.freeze-dm td:first-child{box-shadow:2px 0 4px -2px rgba(0,0,0,.10)}
/* ===== v2 图表筛选 pill ===== */
.filter-pill{height:28px;padding:0 12px;border:1px solid var(--line);border-radius:14px;background:#fff;font-size:12px;color:var(--ink);cursor:pointer;transition:all .15s}
.filter-pill:hover{border-color:var(--brand2);color:var(--brand2)}
.filter-pill.on{background:var(--brand2);border-color:var(--brand2);color:#fff;font-weight:600}
.m3-filter{display:flex;flex-wrap:wrap;gap:8px;align-items:center;margin:10px 0 6px}
.m3-filter .filter-label{font-size:12px;color:var(--ink2);font-weight:600}
/* ===== v2 紧凑头部+可收起侧边栏 ===== */
.page-head{align-items:center;margin-bottom:10px;padding:10px 12px}
.page-head h2{font-size:17px}
.page-head .sub{font-size:11px;margin-top:1px}
.page-head .toolbar{display:flex;align-items:center;gap:8px;flex-wrap:wrap}
.filter-bar{display:inline-flex;gap:8px;padding:6px 10px;margin:0;border:none;background:transparent;box-shadow:none}
.filter-bar label{font-size:11.5px}
.filter-bar select{height:28px;font-size:12px}
.mod-nav{padding:8px 12px;margin-bottom:10px}
.mod-empty{padding:48px 16px}
.layout{transition:.2s}
.sidebar{transition:.2s}
.sidebar .toggle{position:absolute;right:-18px;top:14px;width:18px;height:42px;background:#16283e;color:#fff;border:none;border-radius:0 6px 6px 0;cursor:pointer;font-size:12px;display:flex;align-items:center;justify-content:center;z-index:10;opacity:.9}
.sidebar .toggle:hover{opacity:1}
.layout.collapsed .sidebar{width:0;padding:0;overflow:hidden;border:none}
.layout.collapsed .sidebar .logo,.layout.collapsed .sidebar .nav,.layout.collapsed .sidebar .foot{opacity:0;pointer-events:none}
.layout.collapsed .main{padding-left:10px}
/* 收起后悬浮展开按钮 */
.sidebar-fab{position:fixed;left:10px;top:14px;z-index:60;display:none;align-items:center;justify-content:center;width:34px;height:36px;background:#16283e;color:#fff;border:none;border-radius:8px;cursor:pointer;font-size:15px;box-shadow:0 2px 8px rgba(0,0,0,.25)}
.sidebar-fab:hover{background:#22385a}
.layout.collapsed ~ .sidebar-fab{display:flex}
/* ===== v2.9 一键刷新数据 ===== */
.btn-refresh{background:#16283e;color:#fff;border-color:#16283e;font-weight:600}
.btn-refresh:hover{background:#22385a;border-color:#22385a;color:#fff}
.btn-refresh.busy{opacity:.55;pointer-events:none}
.btn-refresh .spin{display:inline-block;animation:rfspin 1s linear infinite}
@keyframes rfspin{to{transform:rotate(360deg)}}
.refresh-at{font-size:11.5px;color:var(--ink2);white-space:nowrap;font-variant-numeric:tabular-nums}
.refresh-at b{color:var(--ink);font-weight:700}
/* 刷新失败引导弹窗 */
.rf-modal-mask{position:fixed;inset:0;z-index:200;background:rgba(15,25,40,.45);display:flex;align-items:center;justify-content:center;padding:20px}
.rf-modal{background:#fff;border-radius:12px;max-width:480px;width:100%;padding:22px 24px;box-shadow:0 12px 40px rgba(0,0,0,.3);font-size:13.5px;line-height:1.75;color:var(--ink);max-height:82vh;overflow:auto}
.rf-modal h4{margin:0 0 10px;font-size:15px;display:flex;align-items:center;gap:8px;color:#b3261e}
.rf-modal p{margin:6px 0}
.rf-modal .rf-tip{background:#f4f7fb;border-left:3px solid #3b82f6;padding:10px 12px;border-radius:0 8px 8px 0;margin:10px 0;color:var(--ink2)}
.rf-modal a.rf-link{display:inline-block;background:#16283e;color:#fff;padding:7px 14px;border-radius:7px;text-decoration:none;font-weight:600;font-size:13px;margin:6px 0}
.rf-modal a.rf-link:hover{background:#22385a;color:#fff}
.rf-modal .rf-close{margin-top:14px;width:100%;height:34px;border:none;border-radius:7px;background:#eef2f7;cursor:pointer;font-size:13px;color:var(--ink);font-weight:600}
.rf-modal .rf-close:hover{background:#e2e9f2}
.rf-modal .rf-tech{margin-top:10px;font-size:11.5px;color:var(--ink3);word-break:break-all;max-height:90px;overflow:auto;background:#f7f9fb;padding:6px 8px;border-radius:6px}
/* ===== v2.9.2 待开发占位（④ 244客户进展 / ⑤ 出诊地图） ===== */
.wip-box{padding:72px 20px;text-align:center;color:var(--ink3)}
.wip-box .big{font-size:46px;margin-bottom:12px;filter:grayscale(.15)}
.wip-box .wip-t{font-size:19px;font-weight:700;color:var(--ink2);letter-spacing:6px}
.wip-box .wip-s{font-size:12.5px;margin-top:8px}
/* ===== v3 重点医院概览：可排序表格 + 洞察卡 ===== */
.hosp-tbl th{cursor:pointer;user-select:none;white-space:nowrap}
.hosp-tbl th.num{text-align:right}
.hosp-tbl th:hover{background:#eef3fa}
.hosp-tbl th .arr{font-size:9px;opacity:.7;margin-left:2px}
.hosp-tbl tr.hrow{cursor:pointer}
.hosp-tbl tr.hrow:hover td{background:#f2f7fd}
.hosp-tbl tr.sum td{background:#f7faff;font-weight:700}
.hosp-tbl td.num{font-variant-numeric:tabular-nums}
.insight-grid{display:grid;grid-template-columns:repeat(2,1fr);gap:12px;margin-top:14px}
@media (max-width:1100px){.insight-grid{grid-template-columns:1fr}}
.insight-item{background:#fff;border:1px solid var(--line);border-radius:10px;padding:12px 14px}
.insight-item h4{margin:0 0 6px;font-size:12.5px;color:var(--ink2);display:flex;align-items:center;gap:6px;font-weight:700}
.insight-item p{margin:0;font-size:12.5px;line-height:1.75;color:var(--ink);white-space:pre-wrap}
.hosp-tbl-wrap{max-height:62vh;overflow:auto}
/* ===== 客户进展 ===== */
.m8-filter{display:flex;align-items:center;gap:8px;margin:6px 0 10px;flex-wrap:wrap}
.m8-filter label{font-size:12px;color:var(--ink2)}
.m8-filter select{height:30px;border:1px solid var(--line);border-radius:6px;padding:0 8px;font-size:12.5px;background:#fff;color:var(--ink)}
.m8-count{font-size:12px;color:var(--ink2);font-weight:600}
.m8-tbl tr.hl td{background:#fff8e6;font-weight:600}
.m8-tbl td.num{font-variant-numeric:tabular-nums}
.m8-tbl .z{color:var(--ink3)}
.m8-chips{display:flex;gap:8px;flex-wrap:wrap;margin-top:14px;align-items:center}
.m8-chip{height:28px;padding:0 13px;border:1px solid var(--line);border-radius:14px;background:#fff;font-size:12px;color:var(--ink2);cursor:pointer;transition:all .15s}
.m8-chip:hover{border-color:#16283e}
.m8-chip.on{background:#16283e;color:#fff;border-color:#16283e;font-weight:600}
.m8-chip .cnt{opacity:.75;margin-left:3px;font-variant-numeric:tabular-nums}
.m8-detail-title{font-size:13px;font-weight:600;color:var(--ink);margin:10px 0 6px}
.m8-legend{display:flex;align-items:center;gap:16px;flex-wrap:wrap;margin-top:10px;font-size:11.5px;color:var(--ink2)}
.m8-legend .m8-note{color:var(--ink3)}
/* ===== v2.7 303项目 双维度表格 ===== */
.m6-tabs{display:flex;gap:8px;margin:10px 0 12px}
.m6-tab{height:30px;padding:0 14px;border:1px solid var(--line);border-radius:15px;background:#fff;font-size:12px;color:var(--ink);cursor:pointer;transition:all .15s}
.m6-tab:hover{border-color:var(--brand2);color:var(--brand2)}
.m6-tab.on{background:var(--brand2);border-color:var(--brand2);color:#fff;font-weight:600}
.m6-dim{display:grid;grid-template-columns:1fr 1fr;gap:14px}
.m6-week{flex:1;min-width:0}
.m6-week h4{margin:0 0 8px;font-size:13px;color:var(--ink);font-weight:700}
.m6-tbl{width:100%;border-collapse:collapse;font-size:11.5px;background:#fff}
.m6-tbl th,.m6-tbl td{border:1px solid #e2e6ec;padding:4px 6px;text-align:left;vertical-align:top}
.m6-tbl th{background:#f7faff;font-weight:600;color:#16283e}
.m6-tbl td{white-space:normal;word-break:break-word}
.m6-tbl tr:nth-child(even){background:#fafbfc}
.m6-section-title td{font-weight:700;background:#fffbe6;color:#7d5a00}
.m6-lists{display:grid;grid-template-columns:repeat(3,1fr);gap:8px;margin-top:10px}
.m6-lists .m6-tbl{font-size:11px}
.m6-lists .m6-tbl th,.m6-lists .m6-tbl td{padding:3px 4px}
@media (max-width:1100px){.m6-dim,.m6-lists{grid-template-columns:1fr}}
"""
html = html.replace("/* ===== 响应式 ===== */", CSS_ADD + "/* ===== 响应式 ===== */")

# ---------- 3) 替换页面1 section HTML ----------
A = '<!-- ============ 页面1：大区数据概览 ============ -->'
B = '<!-- ============ 页面2：重点医院概览 ============ -->'
i, j = html.find(A), html.find(B)
assert i > 0 and j > i, "section markers not found"

NEW_SECTION = """<!-- ============ 页面1：大区数据概览（v2） ============ -->
    <section class="page active" id="page-region">
      <div class="page-head">
        <div>
          <h2>大区数据概览</h2>
          <div class="sub">东二区 · 6 支 DM 团队 · Q3（6-8月）</div>
        </div>
        <div class="toolbar">
          <div class="filter-bar" id="region-filter">
            <label>DM</label><select id="rf-dm" onchange="applyRegionFilter()"><option value="">全部</option></select>
          </div>
          <button class="btn btn-refresh" id="btn-refresh" onclick="refreshData()" title="重新抓取腾讯文档数据源并更新全部模块">🔄 刷新数据</button>
          <span class="refresh-at" id="refresh-at">最后刷新 —</span>
          <span class="trend-tag neutral">⏱ 85.7%</span>
        </div>
      </div>

      <div class="mod-nav" id="mod-nav">
        <span class="nav-tip">📋 模块导览</span>
        <button class="mod-btn" data-m="1" onclick="toggleMod(1)">TTH进度&季度预估进展</button>
        <button class="mod-btn" data-m="3" onclick="toggleMod(3)">TTH预估实际进展</button>
        <button class="mod-btn" data-m="8" onclick="toggleMod(8)">客户进展</button>
        <button class="mod-btn" data-m="4" onclick="toggleMod(4)">④ 244客户进展</button>
        <button class="mod-btn" data-m="5" onclick="toggleMod(5)">⑤ 出诊地图</button>
        <button class="mod-btn" data-m="6" onclick="toggleMod(6)">⑥ 303项目</button>
        <button class="mod-btn" data-m="7" onclick="toggleMod(7)">⑦ 先锋展示</button>
        <span class="grow"></span>
        <button class="mod-btn collapse" onclick="toggleMod(0)">✕ 收起</button>
      </div>
      <div class="mod-empty" id="mod-empty">
        <div class="big">🗂</div>
        看板已就绪 — 点击上方模块按钮展开对应内容；再点一次或「✕ 收起」返回空白看板
      </div>

      <!-- ① TTH进度 + ② Q3季度预估（并入） -->
      <div class="mod" id="mod-1" style="display:none">
        <div class="card">
          <div class="c-title">① TTH 进度 <span class="tag">AP9 指标 · W1-W5 折算 / 实际 / 实际达成</span></div>
          <div class="tbl-wrap full" id="m1-tbl"></div>
        </div>
        <div class="card" style="margin-top:14px">
          <div class="c-title">② Q3 季度预估 <span class="tag">AP7/AP8 实际 + AP9 预估</span></div>
          <div class="tbl-wrap full" id="m2-tbl"></div>
        </div>
      </div>

      <!-- TTH预估实际进展 -->
      <div class="mod" id="mod-3" style="display:none">
      <div class="card">
        <div class="c-title">TTH预估实际进展 <span class="tag">腾讯文档 分DM日均tth 直接读取</span></div>
        <div class="c-title" style="font-size:13px;margin-top:8px">TTH 预估目标</div>
        <div class="tbl-wrap full" id="m3-target"></div>
        <div class="c-title" style="font-size:13px;margin-top:18px">TTH 预估 — 周均</div>
        <div class="m3-filter" id="m3-filter">
          <span class="filter-label">选择：</span>
          <button class="filter-pill on" data-dm="全部" onclick="setM3Dm('全部')">全部</button>
          <button class="filter-pill" data-dm="孟鈃" onclick="setM3Dm('孟鈃')">孟鈃</button>
          <button class="filter-pill" data-dm="郑家成" onclick="setM3Dm('郑家成')">郑家成</button>
          <button class="filter-pill" data-dm="何方禹" onclick="setM3Dm('何方禹')">何方禹</button>
          <button class="filter-pill" data-dm="李路" onclick="setM3Dm('李路')">李路</button>
          <button class="filter-pill" data-dm="张鑫" onclick="setM3Dm('张鑫')">张鑫</button>
          <button class="filter-pill" data-dm="卜先峰" onclick="setM3Dm('卜先峰')">卜先峰</button>
        </div>
        <div class="chart-box h360" id="c-m3"><canvas></canvas></div>
      </div>
      </div>

      <!-- ④ 244客户进展（v2.9.2 改为待开发占位，原渲染函数 renderM4 保留备用） -->
      <div class="mod" id="mod-4" style="display:none">
      <div class="card">
        <div class="c-title">④ 244 客户进展 <span class="tag">规划中</span></div>
        <div class="wip-box"><div class="big">🚧</div><div class="wip-t">待开发</div><div class="wip-s">本模块正在规划中 · 原数据渲染已暂缓</div></div>
      </div>
      </div>

      <!-- ⑤ 出诊地图（v2.9.2 由「团队跟进」改名，待开发占位，原渲染函数 renderM5 保留备用） -->
      <div class="mod" id="mod-5" style="display:none">
      <div class="card">
        <div class="c-title">⑤ 出诊地图 <span class="tag">规划中</span></div>
        <div class="wip-box"><div class="big">🗺️</div><div class="wip-t">待开发</div><div class="wip-s">出诊地图模块正在规划中 · 敬请期待</div></div>
      </div>
      </div>

      <!-- ⑥ 303项目 -->
      <div class="mod" id="mod-6" style="display:none">
      <div class="card">
        <div class="c-title">⑥ 303 项目进展 <span class="tag">腾讯文档 303项目 直接读取</span></div>
        <div class="m6-tabs">
          <button class="m6-tab on" data-tab="emp" onclick="setM6Tab('emp')">员工维度</button>
          <button class="m6-tab" data-tab="cust" onclick="setM6Tab('cust')">客户维度</button>
        </div>
        <div class="m6-panel" id="m6-emp"></div>
        <div class="m6-panel" id="m6-cust" style="display:none"></div>
      </div>
      </div>

      <!-- ⑦ 先锋展示 -->
      <div class="mod" id="mod-7" style="display:none">
      <div class="card">
        <div class="c-title">⑦ 先锋展示 <span class="tag">图片存本机 IndexedDB · 数量不限 · 可上传/删除/恢复默认</span>
          <span style="flex:1"></span>
          <button class="btn" onclick="document.getElementById('pio-file').click()">＋ 上传图片</button>
          <input type="file" id="pio-file" accept="image/*" multiple style="display:none" onchange="pioUpload(this)">
          <button class="btn" onclick="pioReset()">↺ 恢复默认</button>
        </div>
        <div class="pio-grid" id="pio-grid"></div>
      </div>
      </div>

      <!-- 客户进展（瞄准镜全量） -->
      <div class="mod" id="mod-8" style="display:none">
      <div class="card">
        <div class="c-title">客户进展 <span class="tag">瞄准镜全量 · 区域规则阈值 · 月纯销→观念</span></div>
        <div class="m8-filter">
          <label>月份</label>
          <select id="m8-month" onchange="renderM8()"></select>
          <label>DM</label>
          <select id="m8-dm" onchange="renderM8()"><option value="">全部（含顶部筛选）</option></select>
          <label>客户类型</label>
          <select id="m8-ctype" onchange="renderM8()"><option value="">全部类型</option></select>
          <label>观念</label>
          <select id="m8-cpt" onchange="renderM8()"><option value="">全部观念</option></select>
          <label>亚专业</label>
          <select id="m8-sub" onchange="renderM8()"><option value="">全部亚专业</option></select>
          <span class="grow"></span>
          <span class="m8-count" id="m8-count"></span>
        </div>
        <div class="kpi-grid" id="m8-cards" style="grid-template-columns:repeat(7,1fr);margin-bottom:12px"></div>
        <div class="grid-2">
          <div class="chart-box h260" id="c-m8"><canvas></canvas></div>
          <div class="chart-box h260" id="c-m8-trend"><canvas></canvas></div>
        </div>
        <div class="chart-box" id="c-m8-dm" style="display:none;margin-top:14px;height:310px;padding-top:24px">
          <div class="c-subtitle">分 DM 观念分布（并列 · 仅全部 DM 时显示）</div>
          <canvas></canvas>
        </div>
        <div class="tbl-wrap thin" style="margin-top:12px" id="m8-month-tbl"></div>
        <div class="tbl-wrap thin" style="margin-top:12px" id="m8-sub-tbl"></div>
        <div class="m8-chips" id="m8-chips"></div>
        <div class="tbl-wrap thin" style="margin-top:8px" id="m8-detail"></div>
        <div class="m8-legend">
          <span><b>升级</b>：本月层级 &gt; 上月</span>
          <span><b>降级</b>：本月层级 &lt; 上月</span>
          <span><b>维稳</b>：有销量且层级不变</span>
          <span><b>破冰</b>：上月纯销 0 → 本月有纯销</span>
          <span><b>脱落</b>：上月有纯销 → 本月纯销 0</span>
          <span><b>未破冰</b>：本月与上月纯销均为 0</span>
          <span class="m8-note">观念规则：0=不管不治 · 1–29=阶梯治疗 · 30–69=止痛优选 · 70–129=短期治痛 · 130–299=治痛管理 · 300–499=资深治痛管理 · ≥500=治痛管理大师</span>
        </div>
      </div>
      </div>
    </section>

    """
html = html[:i] + NEW_SECTION + html[j:]

# ---------- 4) 替换 const D ----------
lines = html.split("\n")
for k, ln in enumerate(lines):
    if ln.startswith("const D = "):
        lines[k] = "const D = " + json.dumps(data, ensure_ascii=False, separators=(",", ":")) + ";"
        break
else:
    sys.exit("const D line not found")
html = "\n".join(lines)

# ---------- 5) 替换页面1 JS ----------
JA = "/* ============================================================\n   页面1：大区数据概览\n   ============================================================ */"
JB = "function download(name,content){"
i, j = html.find(JA), html.find(JB)
assert i > 0 and j > i, "js markers not found"

NEW_JS = r"""/* ============================================================
   页面1：大区数据概览（v2 · 7模块）
   ============================================================ */
let rgState={dm:"",mics:"",mod:0,m3Dm:"全部"};
function setM3Dm(d){
  rgState.m3Dm=d;
  document.querySelectorAll("#m3-filter .filter-pill").forEach(b=>b.classList.toggle("on",b.getAttribute("data-dm")===d));
  renderM3();
}
const DM_ORDER=["何方禹","孟鈃","郑家成","李路","张鑫","卜先峰"];
const CLR_DM={"何方禹":"#3b82f6","孟鈃":"#8b5cf6","郑家成":"#0ea5e9","李路":"#14b8a6","张鑫":"#f59e0b","卜先峰":"#ef4444"};
const CLR_TYPE={"A":"#1f5fbf","B":"#3b82f6","C":"#7fb0f2","D":"#bcd3f5"};
const CLR_CON={"不管不治":"#9aa7b5","阶梯治疗":"#d9a514","止痛优选":"#f59e0b","短期治痛":"#3b82f6","治痛管理":"#14b8a6","资深治痛管理":"#8b5cf6","治痛管理大师":"#e4572e"};
const V=D.v2;
if(typeof ChartDataLabels!=="undefined"){Chart.register(ChartDataLabels);Chart.defaults.plugins.datalabels={display:false};}
function initRegion(){
  const rf=document.getElementById("rf-dm");
  DM_ORDER.forEach(d=>{const o=document.createElement("option");o.value=d;o.textContent=d;rf.appendChild(o);});
  restoreRefreshState();
  fmtRefreshAt();
  pioLoad();
  applyRegionFilter();
}
/* ---------- v2.9 一键刷新数据（本地刷新服务 localhost:8787） ---------- */
/* v2.9.1：多地址探测（当前origin:8787 → localhost → 127.0.0.1），失败时弹窗引导正确打开方式 */
let RF_API_BASE=null;
function rfCandidateApis(){
  const list=[];
  if(location.protocol==="http:"&&location.port==="8787")list.push(location.origin+"/api");
  list.push("http://localhost:8787/api","http://127.0.0.1:8787/api");
  return Array.from(new Set(list));
}
function rfFetch(url,opt,timeout){
  return new Promise((resolve,reject)=>{
    let done=false,t=null;
    const fin=(fn,v)=>{if(!done){done=true;if(t)clearTimeout(t);fn(v);}};
    if(typeof AbortController!=="undefined"){
      const ctl=new AbortController();
      t=setTimeout(()=>{ctl.abort();fin(reject,new Error("请求超时"));},timeout||8000);
      fetch(url,Object.assign({},opt||{},{signal:ctl.signal})).then(r=>fin(resolve,r)).catch(e=>fin(reject,e));
    }else{
      t=setTimeout(()=>fin(reject,new Error("请求超时")),timeout||8000);
      fetch(url,opt||{}).then(r=>fin(resolve,r)).catch(e=>fin(reject,e));
    }
  });
}
async function rfFindApi(){
  if(RF_API_BASE)return RF_API_BASE;
  for(const base of rfCandidateApis()){
    try{
      const r=await rfFetch(base+"/status",{method:"GET"},3500);
      if(r.ok){RF_API_BASE=base;return base;}
    }catch(e){}
  }
  return null;
}
function fmtRefreshAt(){
  const el=document.getElementById("refresh-at");
  if(el&&D.refreshed_at)el.innerHTML="最后刷新 <b>"+D.refreshed_at+"</b>";
}
function rfResetBtn(){
  const btn=document.getElementById("btn-refresh");
  if(btn){btn.classList.remove("busy");btn.innerHTML="🔄 刷新数据";}
}
function rfModal(html){
  const old=document.getElementById("rf-modal-mask");
  if(old)old.remove();
  const m=document.createElement("div");
  m.id="rf-modal-mask";m.className="rf-modal-mask";
  m.innerHTML='<div class="rf-modal">'+html+'</div>';
  m.addEventListener("click",e=>{if(e.target===m)m.remove();});
  document.body.appendChild(m);
}
function rfCloseModal(){const m=document.getElementById("rf-modal-mask");if(m)m.remove();}
function rfShowConnErr(e){
  const url="http://localhost:8787/东二区数据看板.html";
  rfModal(
    '<h4>⚠️ 无法连接刷新服务（localhost:8787）</h4>'+
    '<div class="rf-tip">可能原因：<br>① 刷新服务未启动；<br>② 当前看板是以<b>预览 / 直接双击文件</b>方式打开，该环境可能禁止连接本地服务。</div>'+
    '<p><b>方式一（推荐）：</b>在正确地址打开看板后刷新：</p>'+
    '<a class="rf-link" href="'+url+'" target="_blank" rel="noopener">🌐 在刷新服务中打开看板</a>'+
    '<p><b>方式二：</b>双击 <b>「启动刷新服务.command」</b>（在 workbuddy 工作目录），会自动用正确地址打开看板。</p>'+
    '<div class="rf-tech">技术详情：'+(e&&e.message?e.message:String(e))+'</div>'+
    '<button class="rf-close" onclick="rfCloseModal()">知道了</button>'
  );
}
async function refreshData(){
  const btn=document.getElementById("btn-refresh");
  if(btn){btn.classList.add("busy");btn.innerHTML='<span class="spin">🔄</span> 刷新中…';}
  const base=await rfFindApi();
  if(!base){
    rfResetBtn();
    rfShowConnErr(new Error("刷新服务无响应：localhost:8787 与 127.0.0.1:8787 均不可达"));
    return;
  }
  try{
    const r=await rfFetch(base+"/refresh",{method:"POST"},900000);
    const j=await r.json();
    if(j.ok){
      /* 刷新成功：保存当前查看状态 → 重载页面（重新加载新构建的数据） */
      try{localStorage.setItem("dash_v2_refresh",JSON.stringify({mod:rgState.mod,dm:rgState.dm,m3Dm:rgState.m3Dm}));}catch(e){}
      location.reload();
    }else{
      rfResetBtn();
      rfModal(
        '<h4>⚠️ 刷新失败</h4>'+
        '<p><b>'+(j.error||"未知错误")+'</b></p>'+
        '<div class="rf-tech">'+(j.log||"").slice(-800)+'</div>'+
        '<button class="rf-close" onclick="rfCloseModal()">知道了</button>'
      );
    }
  }catch(e){
    rfResetBtn();
    RF_API_BASE=null; /* 下次重新探测 */
    rfShowConnErr(e);
  }
}
function restoreRefreshState(){
  try{
    const s=JSON.parse(localStorage.getItem("dash_v2_refresh")||"null");
    if(!s)return;
    localStorage.removeItem("dash_v2_refresh");
    if(s.dm){const rf=document.getElementById("rf-dm");if(rf)rf.value=s.dm;rgState.dm=s.dm;}
    if(s.m3Dm){
      rgState.m3Dm=s.m3Dm;
      document.querySelectorAll("#m3-filter .filter-pill").forEach(b=>b.classList.toggle("on",b.getAttribute("data-dm")===s.m3Dm));
    }
    if(s.mod)rgState.mod=s.mod;
  }catch(e){}
}
function applyRegionFilter(){
  rgState.dm=document.getElementById("rf-dm").value;
  renderMod();
}
/* ---------- 模块导览：单选展开 / 再点收起 ---------- */
function toggleMod(n){
  rgState.mod=(rgState.mod===n)?0:n;
  renderMod();
}
function renderMod(){
  for(let k=1;k<=8;k++){
    const el=document.getElementById("mod-"+k);
    if(el)el.style.display=(k===rgState.mod)?"":"none";
  }
  const em=document.getElementById("mod-empty");
  if(em)em.style.display=rgState.mod?"none":"";
  document.querySelectorAll("#mod-nav .mod-btn[data-m]").forEach(b=>b.classList.toggle("on",+b.getAttribute("data-m")===rgState.mod));
  const m=rgState.mod;
  if(m===1)renderM1();
  else if(m===2)renderM2();
  else if(m===3)renderM3();
  else if(m===4){/* v2.9.2 待开发占位，不渲染数据 */}
  else if(m===5){/* v2.9.2 出诊地图待开发占位，不渲染数据 */}
  else if(m===6)renderM6();
  else if(m===7)pioRender();
  else if(m===8)renderM8();
}
/* ---------- 客户进展（瞄准镜全量） ---------- */
let m8g="";
let m8s={k:"",d:1};
function m8Sort(k){
  if(m8s.k===k){m8s.d=-m8s.d;}else{m8s.k=k;m8s.d=-1;}  // 首次点击默认降序
  renderM8();
}
const M8N=V.m8_concepts||["不管不治","阶梯治疗","止痛优选","短期治痛","治痛管理","资深治痛管理","治痛管理大师"];
const M8M=V.m8_months||[];
const M8CLR=["#c3ccd6","#a5d8ff","#74c0fc","#4dabf7","#1f5fbf","#7048e8","#2f9e44"];
function m8Fill(id,items,allLabel){
  const s=document.getElementById(id);
  if(s && !s.dataset.filled){
    s.innerHTML='<option value="">'+allLabel+'</option>'+items.map(v=>'<option value="'+v+'">'+v+'</option>').join("");
    s.dataset.filled="1";
  }
}
function renderM8(){
  const mS=document.getElementById("m8-month"),dmS=document.getElementById("m8-dm"),
        ctS=document.getElementById("m8-ctype"),cpS=document.getElementById("m8-cpt"),subS=document.getElementById("m8-sub");
  if(mS && !mS.dataset.filled){
    mS.innerHTML=M8M.map((m,i)=>'<option value="'+i+'">'+m+'</option>').join("");
    mS.value=String(M8M.length-1); mS.dataset.filled="1";
  }
  m8Fill("m8-dm",Array.from(new Set((V.cust_progress||[]).map(x=>x.dm).filter(Boolean))).sort(),"全部（含顶部筛选）");
  m8Fill("m8-ctype",V.ctypes||[],"全部类型");
  m8Fill("m8-cpt",M8N,"全部观念");
  m8Fill("m8-sub",V.subs||[],"全部亚专业");
  const mi=M8M.length?Math.max(0,+mS.value||0):0;
  const dm=dmS?dmS.value:"", ct=ctS?ctS.value:"", cp=cpS?cpS.value:"", sub=subS?subS.value:"";
  const cpv=(cp==="")?-1:M8N.indexOf(cp);
  const rows=(V.cust_progress||[]).filter(x=>
    ((dm||rgState.dm)?x.dm===(dm||rgState.dm):true) &&
    (!ct||x.ctype===ct) && (!sub||x.sub===sub) &&
    (cpv<0 || (x.lvs&&x.lvs[mi]===cpv)));
  /* ---- 卡片：本月 vs 上月 ---- */
  let up=0,down=0,flat=0,ice=0,drop=0,none=0;
  if(mi>0){
    rows.forEach(x=>{const a=x.lvs[mi-1],b=x.lvs[mi];
      const pa=x.tths[mi-1]||0, pb=x.tths[mi]||0;
      const isNoneC=pa===0&&pb===0;
      if(b>a)up++;
      else if(b<a)down++;
      else if(!isNoneC)flat++;   // 维稳：有销量且层级不变（连续两月0销量算未破冰，不算维稳）
      if(pa===0&&pb>0)ice++;      // 破冰：上月纯销0 → 本月有纯销
      if(pa>0&&pb===0)drop++;     // 脱落：上月有纯销 → 本月纯销0
      if(isNoneC)none++;          // 未破冰：连续两月纯销0
    });
  }
  const hasPrev=mi>0;
  const card=(label,val,color,sub2)=>'<div class="kpi"><div class="k-label">'+label+'</div>'+
    '<div class="k-val" style="color:'+color+'">'+val+'</div>'+(sub2?'<div class="k-sub">'+sub2+'</div>':'')+'</div>';
  document.getElementById("m8-cards").innerHTML=
    card("客户总数",rows.length,"#16283e",M8M[mi]+" · "+(hasPrev?("对比 "+M8M[mi-1]):"首月无对比"))+
    card("观念升级",hasPrev?up:"—","#16a34a","本月层级 &gt; 上月")+
    card("观念降级",hasPrev?down:"—","#dc2626","本月层级 &lt; 上月")+
    card("观念维稳",hasPrev?flat:"—","#1f5fbf","有销量且层级不变")+
    card("破冰客户",hasPrev?ice:"—","#ea8a00","上月纯销 0 → 本月有")+
    card("脱落客户",hasPrev?drop:"—","#9c36b5","上月有纯销 → 本月 0")+
    card("未破冰客户",hasPrev?none:"—","#8a99a9","连续两月纯销 0");
  /* ---- 图1：单月观念分布 ---- */
  const dist=M8N.map((n,i)=>rows.filter(x=>x.lvs[mi]===i).length);
  mkChart("c-m8",{type:"bar",data:{labels:M8N.map(n=>n.replace("治痛管理大师","大师").replace("资深治痛管理","资深")),datasets:[{label:"客户数",data:dist,backgroundColor:M8CLR,borderRadius:4}]},
    options:{...baseOpt("客户数"),plugins:{legend:{display:false},datalabels:{display:true,align:"top",anchor:"end",offset:3,color:"#5b6b7c",font:{size:11.5,weight:"700"},formatter:v=>v},tooltip:{callbacks:{label:c=>M8N[c.dataIndex]+"："+c.parsed.y+" 人（"+(rows.length?Math.round(c.parsed.y/rows.length*100):0)+"%）"}}}}});
  /* ---- 图1.5：分 DM 观念分布（仅全部 DM 时显示） ---- */
  const activeDm=dm||rgState.dm;
  const dmBox=document.getElementById("c-m8-dm");
  if(activeDm){
    dmBox.style.display="none";
    if(charts["c-m8-dm"]){charts["c-m8-dm"].destroy();delete charts["c-m8-dm"];}
  }else{
    dmBox.style.display="";
    const dmList=DM_ORDER.filter(d=>rows.some(x=>x.dm===d));
    mkChart("c-m8-dm",{type:"bar",data:{labels:dmList,datasets:M8N.map((n,i)=>({label:n,data:dmList.map(d=>rows.filter(x=>x.dm===d&&x.lvs[mi]===i).length),backgroundColor:M8CLR[i],borderRadius:2}))},
      options:{...baseOpt("客户数"),plugins:{legend:{position:"bottom",labels:{boxWidth:10,font:{size:10.5},color:"#5b6b7c"}},datalabels:{display:c=>(c.dataset.data[c.dataIndex]||0)>0,align:"top",anchor:"end",color:"#5b6b7c",font:{size:9,weight:"600"},formatter:v=>v}},scales:{x:{grid:{display:false},ticks:{font:{size:11},color:"#5b6b7c"}},y:{grid:{color:"#eef1f6"},ticks:{font:{size:11},color:"#5b6b7c"}}}}}
    );
  }
  /* ---- 图2：每月观念分布（堆叠，仅最近4个月） ---- */
  const TREND4=M8M.slice(-4), TSTART=M8M.length-4;
  mkChart("c-m8-trend",{type:"bar",data:{labels:TREND4,datasets:M8N.map((n,i)=>({label:n,data:TREND4.map((m,j)=>rows.filter(x=>x.lvs[TSTART+j]===i).length),backgroundColor:M8CLR[i],borderRadius:2}))},
    options:{...baseOpt("客户数"),plugins:{legend:{position:"bottom",labels:{boxWidth:10,font:{size:10.5},color:"#5b6b7c"}},datalabels:{display:c=>(c.dataset.data[c.dataIndex]||0)>0,align:"top",anchor:"end",color:"#5b6b7c",font:{size:9,weight:"600"},formatter:v=>v}},scales:{x:{grid:{display:false},ticks:{font:{size:10.5},color:"#5b6b7c"}},y:{grid:{color:"#eef1f6"},ticks:{font:{size:11},color:"#5b6b7c"}}}}});
  /* ---- 表1：每月观念分布 ---- */
  const cnt=(j,i)=>rows.filter(x=>x.lvs[j]===i).length;
  let mt='<table class="m8-tbl"><thead><tr><th>月份</th>'+M8N.map(n=>'<th class="num">'+n+'</th>').join("")+'<th class="num">合计</th></tr></thead><tbody>';
  for(let j=M8M.length-1;j>=0;j--){
    mt+='<tr'+(j===mi?' class="hl"':'')+'><td>'+M8M[j]+(j===mi?' ◀':'')+'</td>'+
      M8N.map((n,i)=>{const v=cnt(j,i);return '<td class="num'+(v?'':' z')+'">'+(v||'–')+'</td>';}).join("")+
      '<td class="num"><b>'+rows.length+'</b></td></tr>';
  }
  mt+='</tbody></table>';
  document.getElementById("m8-month-tbl").innerHTML=mt;
  /* ---- 表2：亚专业 × 观念（所选月） ---- */
  const subList=Array.from(new Set(rows.map(x=>x.sub).filter(Boolean))).sort();
  let st='<table class="m8-tbl"><thead><tr><th>亚专业</th>'+M8N.map(n=>'<th class="num">'+n+'</th>').join("")+'<th class="num">合计</th></tr></thead><tbody>';
  subList.forEach(s=>{
    const rs=rows.filter(x=>x.sub===s);
    st+='<tr><td>'+s+'</td>'+M8N.map((n,i)=>{const v=rs.filter(x=>x.lvs[mi]===i).length;return '<td class="num'+(v?'':' z')+'">'+(v||'–')+'</td>';}).join("")+
      '<td class="num"><b>'+rs.length+'</b></td></tr>';
  });
  st+='<tr class="hl"><td>合计</td>'+dist.map(v=>'<td class="num">'+(v||'–')+'</td>').join("")+'<td class="num"><b>'+rows.length+'</b></td></tr></tbody></table>';
  document.getElementById("m8-sub-tbl").innerHTML=st;
  /* ---- 客户明细：按变化类型筛选 ---- */
  const lvUp=x=>hasPrev&&x.lvs[mi]>x.lvs[mi-1];
  const lvDown=x=>hasPrev&&x.lvs[mi]<x.lvs[mi-1];
  const isIce=x=>hasPrev&&(x.tths[mi-1]||0)===0&&(x.tths[mi]||0)>0;
  const isDrop=x=>hasPrev&&(x.tths[mi-1]||0)>0&&(x.tths[mi]||0)===0;
  const isNone=x=>hasPrev&&(x.tths[mi-1]||0)===0&&(x.tths[mi]||0)===0;
  const badgeOf=x=>!hasPrev?["na","—"]:isIce(x)?["ice","破冰"]:isDrop(x)?["drop","脱落"]:isNone(x)?["none","未破冰"]:lvUp(x)?["up","升级"]:lvDown(x)?["down","降级"]:["flat","维稳"];
  const BCSS={"up":"background:rgba(22,163,74,.12);color:#16a34a","down":"background:rgba(220,38,38,.1);color:#dc2626",
    "flat":"background:rgba(31,95,191,.1);color:#1f5fbf","ice":"background:rgba(234,138,0,.14);color:#c46a00",
    "drop":"background:rgba(156,54,181,.12);color:#9c36b5","none":"background:#eef1f6;color:#8a99a9","na":"background:#eef1f6;color:#8a99a9"};
  const chips=[["","全部",rows.length],["up","升级",rows.filter(lvUp).length],["down","降级",rows.filter(lvDown).length],
    ["flat","维稳",rows.filter(x=>hasPrev&&x.lvs[mi]===x.lvs[mi-1]&&!isNone(x)).length],
    ["ice","破冰",rows.filter(isIce).length],["drop","脱落",rows.filter(isDrop).length],
    ["none","未破冰",rows.filter(isNone).length]];
  document.getElementById("m8-chips").innerHTML=chips.map(c=>
    '<button class="m8-chip'+(m8g===c[0]?' on':'')+'" onclick="m8Grp(\''+c[0]+'\')">'+c[1]+'<span class="cnt">'+c[2]+'</span></button>').join("");
  const match=x=>{if(m8g==="")return true;
    if(!hasPrev)return false;
    if(m8g==="up")return lvUp(x);
    if(m8g==="down")return lvDown(x);
    if(m8g==="flat")return x.lvs[mi]===x.lvs[mi-1]&&!isNone(x);
    if(m8g==="ice")return isIce(x);
    if(m8g==="drop")return isDrop(x);
    if(m8g==="none")return isNone(x);
    return true;};
  const ord={"ice":0,"up":1,"down":2,"drop":3,"none":4,"flat":5,"na":6};
  let det=rows.filter(match);
  if(m8s.k){
    const ci=m8s.k==="p"?mi-1:mi;
    det=det.slice().sort((a,b)=>((a.tths[ci]||0)-(b.tths[ci]||0))*m8s.d);
  }else{
    det=det.sort((a,b)=>ord[badgeOf(a)[0]]-ord[badgeOf(b)[0]]||((a.dm||"")+(a.doc||"")).localeCompare((b.dm||"")+(b.doc||"")));
  }
  const arrow=k=>m8s.k===k?(m8s.d<0?" ▼":" ▲"):"";
  const thS=(k,label)=>'<th class="num" style="cursor:pointer;user-select:none" onclick="m8Sort(\''+k+'\')" title="点击排序">'+label+arrow(k)+'</th>';
  let dt='<div class="m8-detail-title">客户明细 · '+(m8g===""?"全部":({up:"升级",down:"降级",flat:"维稳",ice:"破冰",drop:"脱落",none:"未破冰"}[m8g]||m8g))+'（'+det.length+' 位）</div>'+
    '<table class="m8-tbl"><thead><tr><th>医生</th><th>医院</th><th>亚专业</th><th>分型</th><th>DM</th><th>MICS</th>'+
    thS("p","上月纯销")+thS("c","本月纯销")+'<th>上月观念</th><th>本月观念</th><th>变化</th></tr></thead><tbody>';
  det.forEach(x=>{
    const bg=badgeOf(x);
    dt+='<tr><td>'+x.doc+'</td><td>'+x.hosp+'</td><td>'+x.sub+'</td><td>'+x.ctype+'</td><td>'+x.dm+'</td><td>'+x.mics+'</td>'+
      '<td class="num">'+fmt(x.tths[mi-1]||0)+'</td><td class="num"><b>'+fmt(x.tths[mi]||0)+'</b></td>'+
      '<td>'+(hasPrev?M8N[x.lvs[mi-1]]:"—")+'</td><td>'+M8N[x.lvs[mi]]+'</td>'+
      '<td><span class="badge" style="'+BCSS[bg[0]]+'">'+bg[1]+'</span></td></tr>';
  });
  dt+='</tbody></table>';
  document.getElementById("m8-detail").innerHTML=dt;
  document.getElementById("m8-count").textContent="共 "+rows.length+" 位客户 · "+M8M[mi]+" · 观念=当月纯销按区域规则阈值折算";
}
function m8Grp(g){m8g=g;renderM8();}
function pctCell(v){
  if(v==null||isNaN(v))return '<span class="badge pill-gray">—</span>';
  const c=v>=100?"pill-up":(v>=V.time_pct?"pill-warn":"pill-down");
  return '<span class="badge '+c+'">'+fmt(v,1)+'%</span>';
}
/* ---------- ① TTH进度 ---------- */
function renderM1(){
  const tp=V.tth_progress;
  const dms=tp.filter(r=>!rgState.dm||r.dm===rgState.dm);
  const NW=(tp[0].weeks||[]).length;
  let wkHead="";for(let i=0;i<NW;i++){wkHead+='<th class="num">W'+(i+1)+'折算</th><th class="num">W'+(i+1)+'实际</th><th class="num">W'+(i+1)+'实际达成</th>';}
  const head='<table class="freeze-dm"><thead><tr><th>DM</th><th class="num">AP9指标</th><th class="num">目标</th><th class="num">目标进度</th><th class="num">实际</th><th class="num">实际达成</th>'+wkHead+'</tr></thead><tbody>';
  const wk=(r,ix)=>{const w=(r.weeks||[])[ix]||{};
    return '<td class="num">'+(w.tgt!=null?fmt(w.tgt):"—")+'</td><td class="num">'+(w.act!=null?fmt(w.act):"—")+'</td><td class="num">'+(w.rate!=null?fmt(w.rate,1)+"%":"—")+'</td>';};
  const row=(r,hi)=>{let wc="";for(let i=0;i<NW;i++)wc+=wk(r,i);
    return '<tr'+(hi?' class="hi"':'')+'><td><b>'+r.dm+'</b></td><td class="num">'+fmt(r.quota)+'</td><td class="num">'+fmt(r.target)+'</td><td class="num">'+pctCell(r.target_rate)+'</td><td class="num">'+fmt(r.actual)+'</td><td class="num">'+pctCell(r.actual_rate)+'</td>'+wc+'</tr>';};
  const body=head+dms.map(r=>row(r, r.dm==="东二区整体")).join("");
  document.getElementById("m1-tbl").innerHTML=body+"</tbody></table>";
  renderM2();
}
/* ---------- ② 季度预估 ---------- */
function renderM2(){
  const qe=V.quarter_est.filter(r=>!rgState.dm||r.dm===rgState.dm);
  const head='<table class="freeze-dm"><thead><tr><th>DM</th><th class="num">AP7指标</th><th class="num">AP7实际</th><th class="num">达成</th><th class="num">AP8指标</th><th class="num">AP8实际</th><th class="num">达成</th><th class="num">AP9指标</th><th class="num">AP9预估</th><th class="num">达成</th><th class="num">Q3指标</th><th class="num">Q3预估</th><th class="num">Q3达成</th></tr></thead><tbody>';
  const q3q=r=>(r.ap7_quota||0)+(r.ap8_quota||0)+(r.ap9_quota||0);
  const row=r=>'<tr><td><b>'+r.dm+'</b></td><td class="num">'+fmt(r.ap7_quota)+'</td><td class="num">'+fmt(r.ap7_act)+'</td><td class="num">'+pctCell(r.ap7_rate)+'</td><td class="num">'+fmt(r.ap8_quota)+'</td><td class="num">'+fmt(r.ap8_act)+'</td><td class="num">'+pctCell(r.ap8_rate)+'</td><td class="num">'+fmt(r.ap9_quota)+'</td><td class="num">'+fmt(r.ap9_est)+'</td><td class="num">'+pctCell(r.ap9_rate)+'</td><td class="num">'+fmt(q3q(r))+'</td><td class="num"><b>'+fmt(r.q3_est)+'</b></td><td class="num">'+pctCell(r.q3_rate)+'</td></tr>';
  let body=head+qe.map(row).join("");
  if(!rgState.dm&&qe.length){
    const t={};["ap7_quota","ap7_act","ap8_quota","ap8_act","ap9_quota","ap9_est","q3_est"].forEach(k=>t[k]=qe.reduce((a,r)=>a+(r[k]||0),0));
    const rr=(a,b)=>b?Math.round(a/b*1000)/10:null;
    body+='<tr class="hi"><td>合计</td><td class="num">'+fmt(t.ap7_quota)+'</td><td class="num">'+fmt(t.ap7_act)+'</td><td class="num">'+pctCell(rr(t.ap7_act,t.ap7_quota))+'</td><td class="num">'+fmt(t.ap8_quota)+'</td><td class="num">'+fmt(t.ap8_act)+'</td><td class="num">'+pctCell(rr(t.ap8_act,t.ap8_quota))+'</td><td class="num">'+fmt(t.ap9_quota)+'</td><td class="num">'+fmt(t.ap9_est)+'</td><td class="num">'+pctCell(rr(t.ap9_est,t.ap9_quota))+'</td><td class="num">'+fmt(t.ap7_quota+t.ap8_quota+t.ap9_quota)+'</td><td class="num">'+fmt(t.q3_est)+'</td><td class="num">'+pctCell(rr(t.q3_est,t.ap7_quota+t.ap8_quota+t.ap9_quota))+'</td></tr>';
  }
  document.getElementById("m2-tbl").innerHTML=body+"</tbody></table>";
}
/* ---------- TTH预估实际进展 ---------- */
function renderM3(){
  // Part 1: TTH 预估目标 (A1:N8 直接呈现, 源表绿字单元格→看板绿字加粗)
  const t=V.tth_target;
  const G={};(t.green||[]).forEach(g=>{G[g[0]+"_"+g[1]]=g[2];});
  const gStyle=(k)=>G[k]?' style="color:'+G[k]+';font-weight:700"':'';
  let h='<table class="freeze-dm"><thead><tr>'+t.headers.map((x,i)=>'<th'+(i>0?' class="num"':'')+gStyle("0_"+i)+'>'+(x||'')+'</th>').join('')+'</tr></thead><tbody>';
  t.rows.forEach((r,ri)=>{
    h+='<tr'+(ri===t.rows.length-1?' class="hi"':'')+'>'+r.map((c,i)=>{const v=(i===0)?'<b>'+(c||'')+'</b>':(c||'—');return '<td'+(i===0?'':' class="num"')+gStyle((ri+1)+"_"+i)+'>'+v+'</td>';}).join('')+'</tr>';
  });
  document.getElementById("m3-target").innerHTML=h+'</tbody></table>';
  // Part 2: TTH预估——周均 组合图
  const w=V.tth_weekly;
  const dm=rgState.m3Dm==="全部"?"大区总计":rgState.m3Dm;
  const daily=w.daily[dm]||[];
  const weekly=w.weekly[dm]||[];
  const td=w.trend_daily[dm]||[];
  const tw=w.trend_weekly_full[dm]||[];
  // 周均柱放在每周五（周均=周一至周五平均，周末 TTH 已并入下周一）
  const friIdx=(w.fridays||w.mondays||[]).map(m=>w.labels.indexOf(m)).filter(i=>i>=0);
  const barData=w.labels.map((_,i)=>null);
  friIdx.forEach((idx,i)=>{if(idx<barData.length&&i<weekly.length)barData[idx]=weekly[i];});
  const twBar=w.labels.map((_,i)=>null);
  friIdx.forEach((idx,i)=>{if(idx<twBar.length)twBar[idx]=(w.trend_weekly[dm]||[])[i];});
  const fmtLab=v=>v!=null?Math.round(v):'';
  mkChart("c-m3",{
    type:"bar",
    data:{labels:w.labels,datasets:[
      {type:"line",label:"每日",data:daily,borderColor:"#1f5fbf",backgroundColor:"#1f5fbf",borderWidth:2.5,pointRadius:3,pointBackgroundColor:"#fff",pointBorderWidth:2,tension:.1,yAxisID:"y",datalabels:{align:"top",anchor:"end",offset:2,color:"#1f5fbf",font:{size:10,weight:"600"},formatter:fmtLab}},
      {type:"line",label:"线性（每日）",data:td,borderColor:"#1f5fbf",borderWidth:1.5,borderDash:[4,4],pointRadius:0,fill:false,yAxisID:"y",datalabels:{display:false}},
      {type:"bar",label:"周均",data:barData,backgroundColor:"#e8732e",borderRadius:3,barPercentage:.32,yAxisID:"y1",datalabels:{align:"top",anchor:"end",offset:2,color:"#e8732e",font:{size:11,weight:"700"},formatter:fmtLab}},
      {type:"line",label:"线性（周均）",data:tw,borderColor:"#e8732e",borderWidth:1.5,borderDash:[4,4],pointRadius:0,yAxisID:"y1",datalabels:{display:false}}
    ]},
    options:{
      responsive:true,maintainAspectRatio:false,
      interaction:{mode:"index",intersect:false},
      plugins:{
        legend:{position:"bottom",labels:{boxWidth:10,font:{size:11},usePointStyle:true}},
        tooltip:{backgroundColor:"#16283e",titleFont:{size:12},bodyFont:{size:11.5}},
        title:{display:true,text:dm+" TTH日预估变化（"+(w.window?w.window.start+"-"+w.window.end+"，":"")+"周末已并入下周一）",font:{size:15,weight:"bold"},color:"#1c2733",padding:{bottom:10}},
        datalabels:{display:function(ctx){return ctx.dataset.type!=="line"||ctx.dataset.label==="每日";}}
      },
      scales:{
        x:{grid:{display:false},ticks:{font:{size:11},color:"#5b6b7c"}},
        y:{position:"left",title:{display:true,text:"每日",color:"#1f5fbf",font:{size:12,weight:"bold"}},grid:{color:"#eef1f6"},ticks:{font:{size:11},color:"#5b6b7c"}},
        y1:{position:"right",title:{display:true,text:"周均",color:"#e8732e",font:{size:12,weight:"bold"}},grid:{display:false},ticks:{font:{size:11},color:"#5b6b7c"}}
      }
    }
  });
}
/* ---------- ④ 244客户进展 ---------- */
const C244={green_dk:{n:"深绿 · 代言",p:"pill-gdk"},green_lt:{n:"浅绿 · 倡导",p:"pill-glt"},blue:{n:"蓝 · VM",p:"pill-blue"},gray:{n:"灰 · 非目标",p:"pill-gray2"}};
function renderM4(){
  const c=V.cust244.filter(x=>!rgState.dm||x.dm===rgState.dm);
  const cnt=k=>c.filter(x=>x.color===k).length;
  const ok=c.filter(x=>x.rate!=null&&x.rate>=100).length;
  const warn=c.filter(x=>x.rate!=null&&x.rate<V.time_pct*0.7).length;
  const zero=c.filter(x=>x.rate===0).length;
  const t7=c.reduce((a,x)=>a+(x.tth7||0),0),t8=c.reduce((a,x)=>a+(x.tth8||0),0);
  const mom=t7?(t8-t7)/t7*100:null;
  document.getElementById("m4-kpi").innerHTML=[
    mini("追踪客户数",fmt(c.length)),
    mini("深绿 · 代言",fmt(cnt("green_dk"))),
    mini("浅绿 · 倡导",fmt(cnt("green_lt"))),
    mini("蓝 · VM",fmt(cnt("blue"))),
    mini("灰 · 非目标",fmt(cnt("gray"))),
    mini("达标（≥100%）",fmt(ok)),
    mini("严重滞后（<60%）",fmt(warn)),
    mini("8月TTH 环比",fmt(t8)+" "+(mom!=null?fmtPct(mom):"—"))
  ].join("");
  const dms=rgState.dm?[rgState.dm]:DM_ORDER;
  const head='<table><thead><tr><th>DM</th><th class="num">人数</th><th class="num">深绿</th><th class="num">浅绿</th><th class="num">蓝</th><th class="num">灰</th><th class="num">达标</th><th class="num">滞后&lt;60%</th><th class="num">7月TTH</th><th class="num">8月TTH</th><th class="num">环比</th></tr></thead><tbody>';
  let body=head;
  dms.forEach(d=>{
    const s=V.c244_by_dm[d];if(!s)return;
    const m2=s.tth7?(s.tth8-s.tth7)/s.tth7*100:null;
    body+='<tr><td><b>'+d+'</b></td><td class="num">'+fmt(s.n)+'</td><td class="num">'+fmt(s.green_dk)+'</td><td class="num">'+fmt(s.green_lt)+'</td><td class="num">'+fmt(s.blue)+'</td><td class="num">'+fmt(s.gray)+'</td><td class="num">'+fmt(s.ok)+'</td><td class="num">'+fmt(s.warn)+'</td><td class="num">'+fmt(s.tth7)+'</td><td class="num">'+fmt(s.tth8)+'</td><td class="num">'+(m2!=null?'<span class="'+(m2>=0?"badge pill-up":"badge pill-down")+'">'+fmtPct(m2)+'</span>':"—")+'</td></tr>';});
  const tt=V.c244_total;
  if(!rgState.dm) body+='<tr style="background:#f7faff;font-weight:700"><td>合计</td><td class="num">'+fmt(tt.n)+'</td><td class="num">'+fmt(tt.green_dk)+'</td><td class="num">'+fmt(tt.green_lt)+'</td><td class="num">'+fmt(tt.blue)+'</td><td class="num">'+fmt(tt.gray)+'</td><td class="num">'+fmt(tt.ok)+'</td><td class="num">'+fmt(tt.warn)+'</td><td class="num">'+fmt(tt.tth7)+'</td><td class="num">'+fmt(tt.tth8)+'</td><td class="num">'+(mom!=null?'<span class="'+(mom>=0?"badge pill-up":"badge pill-down")+'">'+fmtPct(mom)+'</span>':"—")+'</td></tr>';
  document.getElementById("m4-dm").innerHTML=body+"</tbody></table>";
  mkChart("c-m4",{type:"bar",data:{labels:dms.filter(d=>V.c244_by_dm[d]),datasets:[
    {label:"深绿·代言",data:dms.map(d=>(V.c244_by_dm[d]||{}).green_dk||0),backgroundColor:"#2e7d32",borderRadius:2,stack:"s"},
    {label:"浅绿·倡导",data:dms.map(d=>(V.c244_by_dm[d]||{}).green_lt||0),backgroundColor:"#a5d6a7",borderRadius:2,stack:"s"},
    {label:"蓝·VM",data:dms.map(d=>(V.c244_by_dm[d]||{}).blue||0),backgroundColor:"#1f5fbf",borderRadius:2,stack:"s"},
    {label:"灰·非目标",data:dms.map(d=>(V.c244_by_dm[d]||{}).gray||0),backgroundColor:"#c6cfda",borderRadius:2,stack:"s"}
  ]},options:{...baseOpt("客户数"),plugins:{legend:{position:"bottom",labels:{boxWidth:10,font:{size:10.5}}},tooltip:{backgroundColor:"#16283e"}},scales:{x:{stacked:true,grid:{display:false}},y:{stacked:true,grid:{color:"#eef1f6"}}}}});
  const dh='<table><thead><tr><th>DM</th><th>MICS</th><th>医院</th><th>标签</th><th>医生</th><th>亚专业</th><th>分型</th><th>当前观念</th><th>目标观念</th><th>颜色</th><th class="num">目标</th><th class="num">7月TTH</th><th class="num">8月TTH</th><th class="num">达成率</th></tr></thead><tbody>';
  const drow=x=>{const cc=C244[x.color]||C244.gray;
    return '<tr><td>'+x.dm+'</td><td>'+x.mics+'</td><td>'+x.hosp+'</td><td>'+x.tag+'</td><td><b>'+x.doc+'</b></td><td>'+(x.sub||"")+'</td><td>'+x.ctype+'</td><td>'+x.cpt_now+'</td><td>'+x.cpt_tgt+'</td><td><span class="pill-c '+cc.p+'">'+cc.n+'</span></td><td class="num">'+(x.tgt!=null?fmt(x.tgt):"—")+'</td><td class="num">'+(x.tth7!=null?fmt(x.tth7):"—")+'</td><td class="num">'+(x.tth8!=null?fmt(x.tth8):"—")+'</td><td class="num">'+(x.rate!=null?fmt(x.rate,1)+"%":"—")+'</td></tr>';};
  document.getElementById("m4-detail").innerHTML=dh+c.map(drow).join("")+"</tbody></table>";
}
/* ---------- ⑤ 团队跟进 ---------- */
function cptAgg(cp){
  const g=k=>(cp&&cp[k])||0;
  return {dy:g("代言")+g("超级代言"),cd:g("倡导"),cf:g("重复"),pb:g("破冰/尝试")+g("破冰")+g("尝试")+g("破冰尝试"),wb:g("未破冰")};
}
function renderM5(){
  const dms=DM_ORDER.filter(d=>!rgState.dm||d===rgState.dm);
  const head='<table><thead><tr><th>DM</th><th class="num">MICS数</th><th class="num">跟进客户</th><th class="num">目标合计</th><th class="num">当月预估</th><th class="num">达成率</th><th class="num">代言</th><th class="num">倡导</th><th class="num">重复</th><th class="num">破冰/尝试</th><th class="num">未破冰</th><th class="num">GD</th><th class="num">LB</th><th class="num">SF</th><th class="num">PIM</th></tr></thead><tbody>';
  let body=head;
  let tN=0,tT=0,tE=0;
  dms.forEach(d=>{
    const s=V.team_summary[d];if(!s)return;
    const a=cptAgg(s.cpt);
    tN+=s.n;tT+=s.target||0;tE+=s.est||0;
    body+='<tr><td><b>'+d+'</b></td><td class="num">'+fmt(s.mics_n)+'</td><td class="num">'+fmt(s.n)+'</td><td class="num">'+fmt(s.target)+'</td><td class="num">'+fmt(s.est)+'</td><td class="num">'+pctCell(s.rate)+'</td><td class="num">'+fmt(a.dy)+'</td><td class="num">'+fmt(a.cd)+'</td><td class="num">'+fmt(a.cf)+'</td><td class="num">'+fmt(a.pb)+'</td><td class="num">'+fmt(a.wb)+'</td><td class="num">'+nv2(s.gd)+'</td><td class="num">'+nv2(s.lb)+'</td><td class="num">'+nv2(s.sf)+'</td><td class="num">'+nv2(s.pim)+'</td></tr>';});
  if(!rgState.dm) body+='<tr style="background:#f7faff;font-weight:700"><td>合计</td><td class="num">—</td><td class="num">'+fmt(tN)+'</td><td class="num">'+fmt(tT)+'</td><td class="num">'+fmt(tE)+'</td><td class="num">'+pctCell(tT?tE/tT*100:null)+'</td><td class="num"></td><td class="num"></td><td class="num"></td><td class="num"></td><td class="num"></td><td class="num"></td><td class="num"></td><td class="num"></td><td class="num"></td></tr>';
  document.getElementById("m5-sum").innerHTML=body+"</tbody></table>";
  const rows=V.team.filter(x=>!rgState.dm||x.dm===rgState.dm);
  const dh='<table><thead><tr><th>DM</th><th>MICS</th><th>医院</th><th>医生</th><th>科室</th><th>分型</th><th>观念</th><th class="num">5月TTH</th><th class="num">8月预估</th><th class="num">目标</th><th class="num">达成率</th><th class="num">W1</th><th class="num">W2</th><th class="num">W3</th><th class="num">W4</th><th class="num">GD</th><th class="num">LB</th><th class="num">SF</th><th>本周计划</th></tr></thead><tbody>';
  const drow=x=>{
    const rate=x.target?Math.round((x.month_est||0)/x.target*1000)/10:null;
    const planTxt=[x.wk1_plan?"W1："+x.wk1_plan:"",x.wk2_plan?"W2："+x.wk2_plan:"",x.wk3_plan?"W3："+x.wk3_plan:"",x.wk4_plan?"W4："+x.wk4_plan:""].filter(Boolean).join("\n");
    return '<tr title="'+(planTxt||"").replace(/"/g,"'")+'"><td>'+x.dm+'</td><td>'+x.mics+'</td><td>'+x.hosp+'</td><td><b>'+x.name+'</b></td><td>'+(x.dept||"")+'</td><td>'+(x.ctype||"")+'</td><td>'+(x.concept||"")+'</td><td class="num">'+nv2(x.tth5)+'</td><td class="num">'+nv2(x.month_est)+'</td><td class="num">'+nv2(x.target)+'</td><td class="num">'+(rate!=null?fmt(rate,1)+"%":"—")+'</td><td class="num">'+nv2(x.w1)+'</td><td class="num">'+nv2(x.w2)+'</td><td class="num">'+nv2(x.w3)+'</td><td class="num">'+nv2(x.w4)+'</td><td class="num">'+nv2(x.gd)+'</td><td class="num">'+nv2(x.lb)+'</td><td class="num">'+nv2(x.sf)+'</td><td style="max-width:220px;overflow:hidden;text-overflow:ellipsis" title="'+(x.wk4_plan||x.wk3_plan||x.wk2_plan||x.wk1_plan||"").replace(/"/g,"'")+'">'+(x.wk4_plan||x.wk3_plan||x.wk2_plan||x.wk1_plan||"—")+'</td></tr>';};
  document.getElementById("m5-detail").innerHTML=dh+rows.map(drow).join("")+"</tbody></table>";
}
function nv2(v){return v!=null&&v!==""?fmt(v):"—";}
/* ---------- ⑥ 303项目 ---------- */
function cellHtml(c, tag){
  const v=c.v||"";
  let style="";
  if(c.bg) style+="background-color:"+c.bg+";";
  if(c.fg) style+="color:"+c.fg+";";
  if(c.bold) style+="font-weight:700;";
  return "<"+tag+(style?' style="'+style+'"':'')+">"+(v||" ")+"</"+tag+">";
}
function rowHtml(r, opts={}){
  const cols=opts.cols||r.length;
  const nonEmpty=r.filter(c=>c.v);
  // 单行只有1个非空值 -> 跨列标题
  if(nonEmpty.length===1 && cols>1){
    const c=nonEmpty[0];
    let style=c.bg?'background-color:'+c.bg+';':'';
    if(c.fg) style+='color:'+c.fg+';';
    if(c.bold) style+='font-weight:700;';
    return '<tr><td colspan="'+cols+'"'+(style?' style="'+style+'"':'')+'>'+(c.v||'')+'</td></tr>';
  }
  const cells=Array.from({length:cols},(_,i)=>r[i]||{v:''});
  if(opts.header) return '<tr>'+cells.map(c=>cellHtml(c,'th')).join('')+'</tr>';
  return '<tr>'+cells.map(c=>cellHtml(c,'td')).join('')+'</tr>';
}
function renderEmpWeek(w){
  const rows=w.rows.map((r,i)=>{
    // 表头行：DM/MICS/入职/备注
    if(r.some(c=>c.v==="DM") && r.some(c=>c.v==="MICS")) return rowHtml(r,{header:true,cols:4});
    // 过滤全空行
    if(r.every(c=>!c.v)) return '';
    return rowHtml(r,{cols:4});
  }).join('');
  return '<div class="m6-week"><h4>'+w.title+'</h4><table class="m6-tbl">'+rows+'</table></div>';
}
function renderCustWeek(w){
  const sumRows=w.summary.map((r,i)=>{
    // 表头行
    if(r.some(c=>c.v==="DM") && r.some(c=>c.v.indexOf("连续两周")>=0)) return rowHtml(r,{header:true,cols:4});
    if(r.every(c=>!c.v)) return '';
    return rowHtml(r,{cols:4});
  }).join('');
  const listsHtml=w.lists.map(lst=>{
    const rows=lst.rows.map((r,i)=>{
      if(r.some(c=>c.v==="DM") && r.some(c=>c.v==="MICS")) return rowHtml(r,{header:true,cols:3});
      if(r.every(c=>!c.v)) return '';
      return rowHtml(r,{cols:3});
    }).join('');
    return '<table class="m6-tbl">'+rows+'</table>';
  }).join('');
  return '<div class="m6-week"><h4>'+w.title+'</h4><table class="m6-tbl">'+sumRows+'</table><div class="m6-lists">'+listsHtml+'</div></div>';
}
function renderM6(){
  const emp=V.p303.emp, cust=V.p303.cust;
  document.getElementById("m6-emp").innerHTML='<div class="m6-dim">'+renderEmpWeek(emp.week2)+renderEmpWeek(emp.week3)+'</div>';
  document.getElementById("m6-cust").innerHTML='<div class="m6-dim">'+renderCustWeek(cust.week2)+renderCustWeek(cust.week3)+'</div>';
}
function setM6Tab(tab){
  document.querySelectorAll(".m6-tab").forEach(b=>b.classList.toggle("on",b.dataset.tab===tab));
  document.getElementById("m6-emp").style.display=tab==="emp"?"block":"none";
  document.getElementById("m6-cust").style.display=tab==="cust"?"block":"none";
}
/* ---------- ⑦ 先锋展示（IndexedDB 存储，数量不限） ---------- */
const PIO_KEY="dzdk_pio_v1";
const PIO_DB="dzdk_pio_db",PIO_STORE="pio";
let pioList=null;
function pioDefaults(){return (V.pio||[]).map(p=>({cap:p.cap,img:p.img}));}
function pioOpen(){
  return new Promise((res,rej)=>{
    const rq=indexedDB.open(PIO_DB,1);
    rq.onupgradeneeded=()=>{if(!rq.result.objectStoreNames.contains(PIO_STORE))rq.result.createObjectStore(PIO_STORE);};
    rq.onsuccess=()=>res(rq.result);
    rq.onerror=()=>rej(rq.error);
  });
}
function pioIdb(mode,fn){
  return pioOpen().then(db=>new Promise((res,rej)=>{
    const tx=db.transaction(PIO_STORE,mode);
    const req=fn(tx.objectStore(PIO_STORE));
    let out=undefined;
    // ⚠️ 关键：只读事务的 get() 结果不会自动传给 tx.oncomplete，必须监听 IDBRequest.onsuccess 取 result
    if(req&&typeof req==="object"&&"result" in req)req.onsuccess=()=>{out=req.result;};
    tx.oncomplete=()=>res(out);tx.onerror=()=>rej(tx.error);tx.onabort=()=>rej(tx.error);
  }));
}
async function pioLoad(){
  try{const v=await pioIdb("readonly",st=>st.get("list"));if(Array.isArray(v)&&v.length)pioList=v;}catch(e){}
  if(!pioList||!pioList.length){
    // 降级1：v3.5 之前存在 localStorage 的旧数据 → 读回并迁入 IndexedDB
    try{
      const s=localStorage.getItem(PIO_KEY);
      if(s){const old=JSON.parse(s);if(Array.isArray(old)&&old.length){pioList=old;pioSave();}}
      localStorage.removeItem(PIO_KEY);
    }catch(e){}
  }
  if(!pioList||!pioList.length){
    // 降级2：IndexedDB 不可用（如部分浏览器 file:// 环境）时的兜底备份键
    try{
      const s=localStorage.getItem(PIO_KEY+"_bak");
      if(s){const bk=JSON.parse(s);if(Array.isArray(bk)&&bk.length)pioList=bk;}
    }catch(e){}
  }
  if(!pioList||!pioList.length)pioList=pioDefaults();
  pioRender();
}
/* IndexedDB 不可用时的兜底：同步写一份到 localStorage（>4MB 时放弃，仅保底不主用） */
function pioBackup(){
  try{
    const s=JSON.stringify(pioList);
    if(s.length<4*1024*1024)localStorage.setItem(PIO_KEY+"_bak",s);
    else localStorage.removeItem(PIO_KEY+"_bak");
  }catch(e){}
}
function pioRender(){
  const g=document.getElementById("pio-grid");if(!g)return;
  if(!pioList||!pioList.length){g.innerHTML='<div class="empty">暂无图片，点击右上角「上传图片」添加</div>';return;}
  g.innerHTML=pioList.map((p,i)=>'<div class="pio-card"><img src="'+p.img+'" alt=""><div class="pio-cap"><span>'+(p.cap||("图片"+(i+1)))+'</span><span class="pio-del" onclick="pioDel('+i+')">✕ 删除</span></div></div>').join("");
}
async function pioSave(){
  try{
    await pioIdb("readwrite",st=>st.put(pioList,"list"));
    pioBackup();
  }catch(e){
    // IndexedDB 不可用 → 退回 localStorage 兜底（容量有限，超出时提示）
    try{
      const s=JSON.stringify(pioList);
      localStorage.setItem(PIO_KEY+"_bak",s);
    }catch(e2){
      alert("保存失败：本机存储不可用或空间不足。\n建议用 Chrome/Edge 打开（Safari 在 file:// 下会限制本地存储）。");
    }
  }
}
function pioDel(i){pioList.splice(i,1);pioSave();pioRender();}
function pioCompress(dataUrl){
  return new Promise(res=>{
    try{
      if(dataUrl.length<1.5*1024*1024){res(dataUrl);return;}
      const img=new Image();
      img.onload=()=>{
        try{
          const MAX=2400;let w=img.width,h=img.height;
          if(Math.max(w,h)>MAX){const k=MAX/Math.max(w,h);w=Math.round(w*k);h=Math.round(h*k);}
          const cv=document.createElement("canvas");cv.width=w;cv.height=h;
          cv.getContext("2d").drawImage(img,0,0,w,h);
          const out=cv.toDataURL("image/jpeg",0.9);
          res(out.length<dataUrl.length?out:dataUrl);
        }catch(e){res(dataUrl);}
      };
      img.onerror=()=>res(dataUrl);
      img.src=dataUrl;
    }catch(e){res(dataUrl);}
  });
}
function pioUpload(inp){
  const fs=[...inp.files];inp.value="";
  if(!fs.length)return;
  if(!Array.isArray(pioList))pioList=pioDefaults();  // 防 pioLoad 异步未完成的竞态
  let chain=Promise.resolve();
  fs.forEach(f=>{chain=chain.then(()=>new Promise(res=>{const r=new FileReader();
    r.onload=()=>{pioCompress(r.result).then(out=>{pioList.push({cap:f.name.replace(/\.[^.]+$/,""),img:out});res();});};
    r.onerror=res;r.readAsDataURL(f);}))});
  chain.then(()=>{pioSave();pioRender();});
}
async function pioReset(){
  try{localStorage.removeItem(PIO_KEY);localStorage.removeItem(PIO_KEY+"_bak");}catch(e){}
  try{await pioIdb("readwrite",st=>st.delete("list"));}catch(e){}
  pioList=pioDefaults();pioSave();pioRender();
}
/* ---------- 导出 ---------- */
function exportCsv(which){
  if(which==="region244"){
    const rows=V.cust244.filter(x=>!rgState.dm||x.dm===rgState.dm);
    const head=["DM","MICS","医院","医院标签","医生","亚专业","分型","当前观念","目标观念","颜色","目标","7月TTH","8月TTH","达成率%"];
    let csv=head.join(",")+"\n";
    const cname={green_dk:"深绿-代言",green_lt:"浅绿-倡导",blue:"蓝-VM",gray:"灰-非目标"};
    rows.forEach(x=>csv+=[x.dm,x.mics,x.hosp,x.tag,x.doc,x.sub||"",x.ctype,x.cpt_now,x.cpt_tgt,cname[x.color]||x.color,x.tgt!=null?x.tgt:"",x.tth7!=null?x.tth7:"",x.tth8!=null?x.tth8:"",x.rate!=null?x.rate:""].join(",")+"\n");
    download("东二区_244客户进展.csv","\ufeff"+csv);
  }else if(which==="regionTeam"){
    const rows=V.team.filter(x=>!rgState.dm||x.dm===rgState.dm);
    const head=["DM","MICS","医院","医生","科室","亚专业","分型","观念","4月TTH","5月TTH","8月预估","目标","W1","W2","W3","W4","GD","LB","SF","PIM","W1计划","W2计划","W3计划","W4计划"];
    let csv=head.join(",")+"\n";
    rows.forEach(x=>csv+=[x.dm,x.mics,x.hosp,x.name,x.dept||"",x.sub||"",x.ctype||"",x.concept||"",x.tth4!=null?x.tth4:"",x.tth5!=null?x.tth5:"",x.month_est!=null?x.month_est:"",x.target!=null?x.target:"",x.w1!=null?x.w1:"",x.w2!=null?x.w2:"",x.w3!=null?x.w3:"",x.w4!=null?x.w4:"",x.gd!=null?x.gd:"",x.lb!=null?x.lb:"",x.sf!=null?x.sf:"",x.pimcall!=null?x.pimcall:"",('"' + (x.wk1_plan||"") + '"').replace(/\n/g," "),('"'+(x.wk2_plan||"")+'"').replace(/\n/g," "),('"'+(x.wk3_plan||"")+'"').replace(/\n/g," "),('"'+(x.wk4_plan||"")+'"').replace(/\n/g," ")].join(",")+"\n");
    download("东二区_团队跟进明细.csv","\ufeff"+csv);
  }else if(which==="hospital"){
    const sel=document.getElementById("hf-hosp").value;
    const rows=sel?D.customers.filter(c=>c.h===sel):D.customers;
    const head=["医院","级别","客户","科室","亚专业","分型","是否list","244标签","专诊","出诊次数","3月TTH","4月TTH","5月TTH","6月TTH","7月TTH","当前观念","目标观念","机会点"];
    let csv=head.join(",")+"\n";
    rows.forEach(c=>csv+=[c.h,c.lv,c.n,c.dept,c.sub,c.tp,c.list,c.t244,c.sc,c.ct,c.tth["3月"]||"",c.tth["4月"]||"",c.tth["5月"]||"",c.tth["6月"]||"",c.tth["7月"]||"",c.c_now,c.c_tgt,(c.opp||"").replace(/,/g,"，")].join(",")+"\n");
    download("东二区_客户明细.csv","\ufeff"+csv);
  }
}
function baseOpt(ylabel){return {responsive:true,maintainAspectRatio:false,plugins:{legend:{labels:{boxWidth:10,font:{size:11},color:"#5b6b7c"}},tooltip:{backgroundColor:"#16283e",titleFont:{size:12},bodyFont:{size:11.5}}},scales:{x:{grid:{display:false},ticks:{font:{size:11},color:"#5b6b7c"}},y:{grid:{color:"#eef1f6"},ticks:{font:{size:11},color:"#5b6b7c"},title:{display:!!ylabel,text:ylabel,font:{size:11},color:"#8a99a9"}}}};}

/* ---------- 侧边栏收起/展开（含悬浮展开按钮） ---------- */
function toggleSidebar(){
  const L=document.getElementById("layout");if(!L)return;
  L.classList.toggle("collapsed");
  const collapsed=L.classList.contains("collapsed");
  const b=document.querySelector(".sidebar .toggle");if(b)b.textContent=collapsed?"▶":"◀";
  const fab=document.getElementById("sbExpand");if(fab)fab.style.display=collapsed?"flex":"none";
}

"""
html = html[:i] + NEW_JS + html[j:]

# ---------- 5) 替换页面2：重点医院概览（v3 重构：可排序表格 + 增强一院一屏） ----------
P2A = '<!-- ============ 页面2：重点医院概览 ============ -->'
i2 = html.find(P2A)
assert i2 > 0, "页面2标记未找到"
j2 = html.find('</section>', i2)
assert j2 > i2, "页面2 section 结束未找到"
NEW_P2 = """<!-- ============ 页面2：重点医院概览（v4 · 内嵌独立复盘看板） ============ -->
    <section class="page" id="page-hospital">
      <iframe id="ho-frame" src="hospital_overview.html" title="重点医院概览复盘看板"
        style="width:100%;height:calc(100vh - 84px);border:0;border-radius:10px;background:#fff;box-shadow:var(--shadow)"></iframe>
    </section>"""
html = html[:i2] + NEW_P2 + html[j2 + len('</section>'):]

# ---------- 6) 替换页面2 JS（hospState 起至 </script> 前） ----------
J2A = 'let hospState='
i3 = html.find(J2A)
assert i3 > 0, "页面2 JS 起点未找到"
j3 = html.find('</script>', i3)
assert j3 > i3, "页面2 JS 结束未找到"
NEW_P2JS = """/* ---------- v3 重点医院概览：可排序表格 + 增强一院一屏 ---------- */
const HMONTHS=["3月","4月","5月","6月","7月","8月"];
let hospState={level:"",dm:"",mics:"",access:""};
let hSort={k:"",d:1};
function hLM(h){return h.latest_month||"7月";}
function hTV(h,m){return h&&h.tth&&h.tth[m]!=null?h.tth[m]:null;}
function initHospFilters(){
  const lv=["TOP","CORE","Growth"];
  const fl=document.getElementById("hf-level");
  lv.forEach(v=>{const o=document.createElement("option");o.value=v;o.textContent=v;fl.appendChild(o);});
  const fdm=document.getElementById("hf-dm");
  DM_ORDER.forEach(d=>{const o=document.createElement("option");o.value=d;o.textContent=d;fdm.appendChild(o);});
  const fa=document.getElementById("hf-access");
  [...new Set(D.hospitals.map(h=>h.access).filter(Boolean))].forEach(v=>{const o=document.createElement("option");o.value=v;o.textContent=v;fa.appendChild(o);});
  const fm=document.getElementById("hf-mics");
  [...new Set(D.hospitals.map(h=>h.mics))].sort().forEach(v=>{const o=document.createElement("option");o.value=v;o.textContent=v;fm.appendChild(o);});
}
function filteredHospitals(){
  return D.hospitals.filter(h=>
    (!hospState.level||h.level===hospState.level)&&
    (!hospState.dm||h.dm===hospState.dm)&&
    (!hospState.mics||h.mics===hospState.mics)&&
    (!hospState.access||h.access===hospState.access));
}
function applyHospFilter(){
  hospState.level=document.getElementById("hf-level").value;
  hospState.dm=document.getElementById("hf-dm").value;
  hospState.mics=document.getElementById("hf-mics").value;
  hospState.access=document.getElementById("hf-access").value;
  const sel=document.getElementById("hf-hosp");const cur=sel.value;
  sel.innerHTML='<option value="">— 请选择医院 —</option>';
  filteredHospitals().forEach(h=>{const o=document.createElement("option");o.value=h.name;o.textContent=h.name;sel.appendChild(o);});
  sel.value=filteredHospitals().some(h=>h.name===cur)?cur:"";
  renderHospTable();
}
function resetHosp(){
  ["hf-level","hf-dm","hf-mics","hf-access"].forEach(id=>document.getElementById(id).value="");
  hospState={level:"",dm:"",mics:"",access:""};
  applyHospFilter();
}
function selectHospital(){
  const name=document.getElementById("hf-hosp").value;
  if(name){ const h=D.hospitals.find(x=>x.name===name); renderHospView(h); }
  else renderHospTable();
}
function sortHosp(k){
  if(hSort.k===k){hSort.d=-hSort.d;}else{hSort.k=k;hSort.d=-1;}
  renderHospTable();
}
function renderHospTable(){
  const hs=filteredHospitals();
  const view=document.getElementById("hosp-view");
  const lmList=D.hospitals.map(h=>hLM(h));
  const lm=lmList[0]||"7月";
  document.getElementById("hosp-sub").textContent=hs.length+" 家重点医院（TOP / CORE / Growth）· 数据截至 "+lm+" · 点击表头排序 · 点击医院行进入「一院一屏」";
  document.getElementById("hosp-summary").innerHTML=`<div class="summary-note">当前筛选：<b>${hs.length}</b> 家医院${hospState.dm?" · DM："+hospState.dm:""}${hospState.level?" · 级别："+hospState.level:""}${hospState.mics?" · MICS："+hospState.mics:""}${hospState.access?" · 准入："+hospState.access:""} — 点击表头排序，点击医院行进入「一院一屏」</div>`;
  if(!hs.length){ view.innerHTML='<div class="empty">无符合条件的医院</div>'; return; }
  const k=hSort.k,d=hSort.d;
  const arr=hs.slice();
  const val=h=>{
    if(k==="name")return h.name;
    if(k==="level")return h.level;
    if(k==="dm")return h.dm;
    if(k==="access")return h.access||"";
    if(k==="net")return h.net!=null?h.net:-1e12;
    if(k==="growth")return h.growth!=null?h.growth:-1e12;
    if(k==="tag")return h.tag_count!=null?h.tag_count:-1e12;
    if(k==="active")return h.active7!=null?h.active7:-1e12;
    if(k&&k.indexOf("月")>0)return hTV(h,k)!=null?hTV(h,k):-1e12;
    return 0;
  };
  if(k){arr.sort((a,b)=>{const va=val(a),vb=val(b);return (typeof va==="string"?String(va).localeCompare(String(vb),"zh"):(va-vb))*d;});}
  const arrMark=(col)=>k===col?`<span class="arr">${d>0?"▲":"▼"}</span>`:"";
  const th=(col,label,cls)=>`<th class="${cls||""}" onclick="sortHosp('${col}')" title="点击排序">${label}${arrMark(col)}</th>`;
  const months=HMONTHS.filter(m=>D.hospitals.some(h=>hTV(h,m)!=null));
  const tagClsOf=(h)=>h.trend_label==="持续增长"?"good":(h.trend_label==="连续下滑"?"bad":(h.trend_label==="波动较大"?"warn":"neutral"));
  const rows=arr.map(h=>{
    const tthCells=months.map(m=>`<td class="num">${fmt(hTV(h,m))}</td>`).join("");
    return `<tr class="hrow" onclick='renderHospView(${JSON.stringify(h).replace(/'/g,"&#39;")})'>
      <td><b>${h.name}</b></td>
      <td><span class="badge ${h.level==="TOP"?"top":(h.level==="CORE"?"core":"growth")}">${h.level}</span></td>
      <td>${h.dm}</td><td style="white-space:nowrap">${h.mics}</td>
      <td style="white-space:nowrap">${h.access||"无记录"}</td>
      ${tthCells}
      <td class="num">${h.net!=null?`<span class="${h.net>=0?"up":"down"}">${h.net>=0?"+":""}${fmt(h.net)}</span>`:"—"}</td>
      <td class="num">${h.growth!=null?fmtPct(h.growth):"—"}</td>
      <td><span class="trend-tag ${tagClsOf(h)}">${h.trend_label}</span></td>
      <td class="num">${fmt(h.tag_count)}</td>
      <td class="num">${fmt(h.active7)}</td>
    </tr>`;
  }).join("");
  const sumCells=months.map(m=>`<td class="num">${fmt(arr.reduce((a,h)=>a+(hTV(h,m)||0),0))}</td>`).join("");
  view.innerHTML=`<div class="card"><div class="tbl-wrap full hosp-tbl hosp-tbl-wrap"><table class="hosp-tbl"><thead><tr>
    ${th("name","医院")}${th("level","级别")}${th("dm","DM")}<th>MICS</th>${th("access","准入")}
    ${months.map(m=>th(m,m+"TTH","num")).join("")}
    ${th("net","净增","num")}${th("growth","增长率","num")}<th>趋势</th>${th("tag","标签客户","num")}${th("active","活跃客户","num")}
  </tr></thead><tbody>${rows}
  <tr class="sum"><td>合计（${arr.length} 家）</td><td colspan="4"></td>${sumCells}<td></td><td></td><td></td><td></td><td></td></tr>
  </tbody></table></div></div>`;
}
function renderHospList(){renderHospTable();}
/* ---------- 一院一屏（v3 增强） ---------- */
function renderHospView(h){
  document.getElementById("hf-hosp").value=h.name;
  const lm=hLM(h);
  document.getElementById("hosp-summary").innerHTML=`<div class="summary-note">🔍 已进入「${h.name}」一院一屏（数据截至 ${lm}），切换筛选器或选择其他医院即可返回列表</div>`;
  const view=document.getElementById("hosp-view");
  const cu=custOf(h.name);
  const bigCu=cu.filter(c=>["治痛管理","资深治痛管理","治痛管理大师"].includes(c.c_now));
  const tagCls=h.trend_label==="持续增长"?"good":(h.trend_label==="连续下滑"?"bad":(h.trend_label==="波动较大"?"warn":"neutral"));
  const trendTag=`<span class="trend-tag ${tagCls}">${h.trend_label}</span>`;
  const activeRate=h.active_rate;
  const rateNote=activeRate!=null&&activeRate>100?'<span style="color:var(--warn);font-size:10.5px">（活跃>标签，名单待补）</span>':"";
  const tv=hTV(h,lm);
  const tPrev=hTV(h,HMONTHS[Math.max(0,HMONTHS.indexOf(lm)-1)]);
  view.innerHTML=`
  <div class="hosp-head">
    <h3>🏥 ${h.name} ${trendTag}</h3>
    <div class="hosp-meta">
      <span class="meta-chip">级别 <b>${h.level}</b></span>
      <span class="meta-chip">DM <b>${h.dm}</b></span>
      <span class="meta-chip">MICS <b>${h.mics}</b></span>
      <span class="meta-chip">准入 <b>${h.access||"无记录"}</b></span>
      <span class="meta-chip">渠道 <b>${h.channel||"—"}</b></span>
      <span class="meta-chip">金额限制 <b>${h.limit||"无"}</b></span>
      <span class="meta-chip">头痛门诊 <b>${fmt(h.headache_clinic)}/周 · ${fmt(h.headache_cust)}客户</b></span>
      <span class="meta-chip">眩晕门诊 <b>${fmt(h.vertigo_clinic)}/周 · ${fmt(h.vertigo_cust)}客户</b></span>
      <span class="meta-chip">梯队 <b>${h.tier||"—"}</b></span>
    </div>
  </div>
  <div class="kpi-grid">
    ${kpi(lm+" TTH",fmt(tv),"vs 前月",`<span class="badge ${(h.mom7??0)>=0?"pill-up":"pill-down"}">${fmtPct(h.mom7)}</span>`)}
    ${kpi("3-"+lm+"净增量",fmt(h.net),(h.net??0)>=0?"持续向好":"需关注",`<span class="${(h.net??0)>=0?"up":"down"}">${(h.net??0)>=0?"▲":"▼"} ${fmt(Math.abs(h.net))}</span>`)}
    ${kpi("3-"+lm+"增长率",fmtPct(h.growth),"",`<span class="badge ${(h.growth??0)>=0?"pill-up":"pill-down"}">${fmtPct(h.growth)}</span>`)}
    ${kpi("标签客户数",fmt(h.tag_count),"瞄准镜名单","")}
    ${kpi("活跃客户("+lm+")",fmt(h.active7),`活跃率 ${fmt(activeRate)}% ${rateNote}`,"")}
    ${kpi("大客户数",fmt(h.big_n),lm+"贡献 "+fmt(h.big_share)+"%","")}
    ${kpi("客户名单(DDD)",fmt(h.cust_n),"客户DDD名单内","")}
    ${kpi("9月TTH目标",fmt(h.tgt9),"Q4梯队:"+(h.q4_tier||"—"),"")}
  </div>
  <div class="grid-1x2" style="margin-top:14px">
    <div class="card">
      <div class="c-title">📈 TTH 预估趋势（3-${lm}）<span class="tag">单位：盒</span></div>
      <div class="chart-box h240" id="c-h-trend"><canvas></canvas></div>
    </div>
    <div class="card">
      <div class="c-title">🔬 变化诊断</div>
      <div class="diag-list">
        ${diag(lm+"环比",fmtPct(h.mom7))}
        ${diag("3-"+lm+"净增量",fmtPct(h.net))}
        ${diag("3-"+lm+"增长率",fmtPct(h.growth))}
        ${diag("最高月份",h.max_month+"（"+fmt(h.trend_series[Math.max(0,HMONTHS.indexOf(h.max_month))])+"）")}
        ${diag("最低月份",h.min_month+"（"+fmt(h.trend_series[Math.max(0,HMONTHS.indexOf(h.min_month))])+"）")}
        ${diag("波动幅度",fmtPct(h.volatility)+"")}
        ${diag("经营状态",`<span class="trend-tag ${tagCls}">${h.trend_label}</span>`)}
      </div>
      ${h.insight?`<div style="margin-top:10px;font-size:11.5px;color:var(--ink2);background:#f7f9fc;padding:8px 10px;border-radius:8px"><b>DDD洞察：</b>${h.insight}</div>`:""}
    </div>
  </div>
  <div class="grid-3">
    <div class="card">
      <div class="c-title">👥 客户基础 <span class="tag">${lm}</span></div>
      <div class="mini-grid">
        ${mini("标签客户",fmt(h.tag_count))}
        ${mini("活跃客户",fmt(h.active7))}
        ${mini("非活跃客户",fmt((h.tag_count??0)-(h.active7??0)))}
        ${mini("C类(VM)",fmt((h.abcd||{}).C))}
      </div>
      <div class="chart-box h160" style="margin-top:10px" id="c-h-abcd"><canvas></canvas></div>
    </div>
    <div class="card">
      <div class="c-title">🧩 A/B/C/D 客户产出 <span class="tag">人数+产出</span></div>
      <div class="chart-box h240" id="c-h-typeperf"><canvas></canvas></div>
    </div>
    <div class="card">
      <div class="c-title">🧠 观念结构（当前 vs 目标）<span class="tag">客户名单</span></div>
      <div class="chart-box h240" id="c-h-concept"><canvas></canvas></div>
    </div>
  </div>
  <div class="grid-3" style="margin-top:14px">
    <div class="card">
      <div class="c-title">🏥 科室 / 亚专业结构</div>
      <div class="chart-box h220" id="c-h-dept"><canvas></canvas></div>
    </div>
    <div class="card">
      <div class="c-title">🎯 出诊次数 × ${lm}TTH 散点 <span class="tag">识别机会</span></div>
      <div class="chart-box h220" id="c-h-scatter"><canvas></canvas></div>
      <div class="legend-row" style="margin-top:6px">
        <span class="lg"><span class="dot" style="background:#3b82f6"></span>高频出诊·高产出=核心维护</span>
        <span class="lg"><span class="dot" style="background:#f59e0b"></span>高频低产=转化机会</span>
      </div>
    </div>
    <div class="card">
      <div class="c-title">📊 观念 × 销量（${lm}）</div>
      <div class="tbl-wrap thin" id="concept-tbl"></div>
    </div>
  </div>
  ${(h.insight||h.strategy||h.plan||h.support)?`<div class="insight-grid">
    <div class="insight-item"><h4>💡 洞察诊断</h4><p>${h.insight||"—"}</p></div>
    <div class="insight-item"><h4>🎯 策略</h4><p>${h.strategy||"—"}</p></div>
    <div class="insight-item"><h4>📈 客户增长计划</h4><p>${h.plan||"—"}</p></div>
    <div class="insight-item"><h4>🤝 所需需求 & 支持</h4><p>${h.support||"—"}</p></div>
  </div>`:""}
  <div class="card" style="margin-top:14px">
    <div class="c-title">📋 全部客户明细（${cu.length} 人 · 按${lm}TTH降序）<span class="tag">绿=增长稳定 · 黄=高潜未转化 · 红=下滑 · 蓝=重点打造</span></div>
    <div class="tbl-wrap" id="cust-tbl"></div>
  </div>
  <div class="card" style="margin-top:14px">
    <div class="c-title">⭐ 重点打造客户（目标观念 ≥ 治痛管理）<span class="tag">${bigCu.length} 人 · ${lm}TTH ${fmt(h.big_tth7)} · 贡献 ${fmt(h.big_share)}%</span></div>
    <div class="tbl-wrap" id="big-tbl"></div>
  </div>
  <div class="advice" id="advice-box"></div>`;
  renderHospCharts(h);
  renderConceptTbl(cu);
  renderCustTable(cu,h);
  renderBigTable(h);
  buildAdvice(h,cu);
}
function kpi(label,val,sub,delta){return `<div class="kpi"><div class="k-label">${label}</div><div class="k-val">${val}</div><div class="k-sub" style="display:flex;align-items:center;gap:6px">${delta||""}${sub||""}</div></div>`;}
function diag(l,v){return `<div class="diag-item"><span class="d-label">${l}</span><span class="d-val">${v}</span></div>`;}
function mini(l,v){return `<div class="mini"><div class="m-label">${l}</div><div class="m-val">${v}</div></div>`;}
function custOf(hname){
  const lm=hLM(D.hospitals.find(x=>x.name===hname)||{});
  return D.customers.filter(c=>c.h===hname)
    .sort((a,b)=>(b.tth[lm]||0)-(a.tth[lm]||0));
}
function renderHospCharts(h){
  const lm=hLM(h);
  const t=h.trend_series;
  const labels=HMONTHS.slice(0,t.length);
  mkChart("c-h-trend",{type:"line",data:{labels,datasets:[{label:"TTH",data:t,borderColor:"#1f5fbf",backgroundColor:"rgba(31,95,191,.1)",fill:true,tension:.3,pointRadius:5,pointBackgroundColor:"#fff",pointBorderColor:"#1f5fbf",pointBorderWidth:2.5,borderWidth:3}]},options:{...baseOpt("TTH（盒）"),plugins:{...baseOpt("").plugins,legend:{display:false},tooltip:{callbacks:{label:c=>`${labels[c.dataIndex]}：${fmt(c.parsed.y)} 盒`}}}}});
  // ABCD客户数
  const abcd=h.abcd;
  mkChart("c-h-abcd",{type:"bar",data:{labels:["A","B","C","D"],datasets:[{label:"客户数",data:["A","B","C","D"].map(k=>abcd[k]||0),backgroundColor:["#1f5fbf","#3b82f6","#7fb0f2","#bcd3f5"],borderRadius:4}]},options:{...baseOpt("客户数"),plugins:{legend:{display:false}}}});
  // 类型产出：最新月TTH + 人均
  const cu=custOf(h.name);
  const types=["A","B","C","D"];
  const perf=types.map(tp=>{
    const cs=cu.filter(c=>c.tp===tp);
    const tth=cs.reduce((a,c)=>a+(c.tth[lm]||0),0);
    const per=cs.length?tth/cs.length:0;
    const m3=cs.reduce((a,c)=>a+(c.tth["3月"]||0),0);
    const g=m3?(tth-m3)/m3*100:null;
    return {tp,n:cs.length,tth,per,g};
  });
  mkChart("c-h-typeperf",{type:"bar",data:{labels:types.map(t=>t+"类"),datasets:[
    {label:lm+"TTH",data:perf.map(p=>p.tth),backgroundColor:types.map(t=>CLR_TYPE[t]),borderRadius:4,yAxisID:"y"},
    {label:"人均TTH",data:perf.map(p=>+p.per.toFixed(1)),type:"line",borderColor:"#e4572e",backgroundColor:"#e4572e",pointRadius:3,tension:.3,yAxisID:"y1"}
  ]},options:{...baseOpt(""),plugins:{legend:{position:"bottom",labels:{boxWidth:10,font:{size:11}}}},scales:{x:{grid:{display:false}},y:{grid:{color:"#eef1f6"},title:{display:true,text:"TTH(盒)"}},y1:{position:"right",grid:{display:false},title:{display:true,text:"人均"}}}}});
  // 观念 当前vs目标
  const cntNow=CONCEPTS.map(c=>cu.filter(x=>x.c_now===c).length);
  const cntTgt=CONCEPTS.map(c=>cu.filter(x=>x.c_tgt===c).length);
  mkChart("c-h-concept",{type:"bar",data:{labels:CONCEPTS.map(c=>c.replace("治痛管理大师","大师")),datasets:[
    {label:"当前",data:cntNow,backgroundColor:CONCEPTS.map(c=>CLR_CON[c]),borderRadius:4},
    {label:"目标",data:cntTgt,backgroundColor:"rgba(31,95,191,.22)",borderColor:"#1f5fbf",borderWidth:1.2,borderRadius:4}
  ]},options:{...baseOpt("客户数"),plugins:{legend:{position:"bottom",labels:{boxWidth:10,font:{size:11}}}}}});
  // 科室/亚专业
  const deptCount={};
  cu.forEach(c=>{const k=c.sub&&c.sub!=="其他"?c.sub:c.dept;deptCount[k]=(deptCount[k]||0)+1;});
  const deptArr=Object.entries(deptCount).sort((a,b)=>b[1]-a[1]).slice(0,8);
  mkChart("c-h-dept",{type:"bar",data:{labels:deptArr.map(d=>d[0]),datasets:[{label:"客户数",data:deptArr.map(d=>d[1]),backgroundColor:"#3b82f6",borderRadius:4}]},options:{...baseOpt("客户数"),indexAxis:"y",plugins:{legend:{display:false}},scales:{x:{grid:{color:"#eef1f6"},ticks:{font:{size:10}}},y:{grid:{display:false},ticks:{font:{size:10.5}}}}}});
  // 散点：出诊次数 x 最新月TTH
  const pts=cu.filter(c=>c.ct!=null&&c.tth[lm]!=null).map(c=>({x:c.ct,y:c.tth[lm],n:c.n}));
  mkChart("c-h-scatter",{type:"scatter",data:{datasets:[{data:pts.map(p=>({x:p.x,y:p.y})),backgroundColor:"#3b82f6",pointRadius:5,pointHoverRadius:7}]},options:{...baseOpt(lm+"TTH(盒)"),plugins:{legend:{display:false},tooltip:{callbacks:{title:it=>{const p=pts[it[0].dataIndex];return p?p.n:"";},label:it=>`出诊${it.parsed.x}次 · TTH ${fmt(it.parsed.y)}`}}},scales:{x:{grid:{color:"#eef1f6"},title:{display:true,text:"出诊次数/月",font:{size:11},color:"#8a99a9"},ticks:{font:{size:11}}},y:{grid:{color:"#eef1f6"},title:{display:true,text:lm+"TTH(盒)",font:{size:11},color:"#8a99a9"},ticks:{font:{size:11}}}}}});
}
function renderConceptTbl(cu){
  const lm=hLM(D.hospitals.find(x=>x.name===document.getElementById("hf-hosp").value)||{});
  const rows=CONCEPTS.map(c=>{
    const cs=cu.filter(x=>x.c_now===c);
    if(!cs.length) return null;
    const tth=cs.reduce((a,x)=>a+(x.tth[lm]||0),0);
    const m3=cs.reduce((a,x)=>a+(x.tth["3月"]||0),0);
    const g=m3?(tth-m3)/m3*100:null;
    return `<tr><td>${c}</td><td class="num">${cs.length}</td><td class="num">${fmt(tth)}</td><td class="num">${fmt(tth/cs.length,1)}</td><td class="num"><span class="${(g??0)>=0?"up":"down"}">${fmtPct(g)}</span></td></tr>`;
  }).filter(Boolean).join("");
  document.getElementById("concept-tbl").innerHTML=`<table><thead><tr><th>观念阶段</th><th class="num">客户数</th><th class="num">${lm}TTH</th><th class="num">人均</th><th class="num">3-${lm}增长</th></tr></thead><tbody>${rows}</tbody></table>`;
}
function renderCustTable(cu,h){
  const lm=hLM(h);
  const rows=cu.map(c=>{
    const t3=c.tth["3月"]||0,tN=c.tth[lm]||0;
    const g=t3?(tN-t3)/t3*100:null;
    let cls="";
    if(c.t244==="是"&&g!=null&&g<=-10) cls="r-down";
    else if(g!=null&&g>=20&&tN>=10) cls="r-up";
    else if(g!=null&&g<=-10&&tN>0) cls="r-warn";
    else if(c.t244==="是"&&g!=null&&g>=0) cls="r-focus";
    const chgHtml=g==null?"—":`<span class="${g>=0?"up":"down"}">${g>=0?"▲":"▼"}${fmtPct(g)}</span>`;
    return `<tr class="${cls}">
      <td><b>${c.n}</b></td><td>${c.dept}</td><td>${c.sub||"—"}</td>
      <td><span class="badge ${c.tp==="A"?"top":(c.tp==="B"?"core":(c.tp==="C"?"growth":"pill-gray"))}">${c.tp}</span></td>
      <td class="center">${c.list==="是"?"✅":""}</td><td class="center">${c.t244==="是"?"⭐":""}</td>
      <td>${c.sc||"—"}</td><td class="num">${fmt(c.ct)}</td>
      <td class="num">${fmt(t3)}</td><td class="num">${fmt(tN)}</td>
      <td class="num">${chgHtml}</td>
      <td>${c.c_now||"—"}</td><td>${c.c_tgt||"—"}</td>
      <td style="white-space:normal;max-width:200px;color:var(--ink3)">${c.opp||""}</td>
      <td style="white-space:normal;max-width:200px;color:var(--ink3)">${c.act||""}</td>
    </tr>`;
  }).join("");
  document.getElementById("cust-tbl").innerHTML=`<table><thead><tr>
    <th>客户</th><th>科室</th><th>亚专业</th><th>分型</th><th class="center">List</th><th class="center">244</th><th>专诊</th><th class="num">出诊/月</th>
    <th class="num">3月TTH</th><th class="num">${lm}TTH</th><th class="num">3-${lm}变化</th><th>当前观念</th><th>目标观念</th><th>机会点</th><th>行动计划</th>
  </tr></thead><tbody>${rows}</tbody></table>`;
}
function renderBigTable(h){
  const lm=hLM(h);
  const bd=D.key_customers.filter(k=>k.h===h.name);
  const rows=(bd||[]).map(k=>{
    const t3=k.tth["3月"]||0,t7=k.tth["7月"]||0;
    const g=t3?(t7-t3)/t3*100:null;
    const gap=k.tgt8?(k.tgt8-t7):null;
    return `<tr>
      <td><b>${k.n}</b></td><td>${k.dm} / ${k.mics}</td><td>${k.dept}·${k.sub||"—"}</td>
      <td class="num">${fmt(t3)}</td><td class="num">${fmt(t7)}</td><td class="num">${fmt(k.tgt8)}</td>
      <td class="num">${gap==null?"—":`<span class="${gap>=0?"up":"down"}">${fmtPct(gap)}</span>`}</td>
      <td>${k.c_now||"—"}</td><td>${k.c_tgt||"—"}</td>
      <td style="white-space:normal;max-width:170px;color:var(--ink3)">${k.opp||""}</td>
      <td style="white-space:normal;max-width:170px;color:var(--ink3)">${k.act||""}</td>
      <td style="white-space:normal;max-width:150px;color:var(--ink3)">${k.sup||""}</td>
    </tr>`;
  }).join("");
  const emptyRows=!rows?`<tr><td colspan="12" class="center" style="padding:18px;color:var(--ink3)">该院暂无「打造大客户名单」记录（名单中 ${D.key_customers.length} 人，覆盖 17 家医院）</td></tr>`:"";
  document.getElementById("big-tbl").innerHTML=`<table><thead><tr>
    <th>客户</th><th>DM / MICS</th><th>科室·亚专业</th><th class="num">3月TTH</th><th class="num">7月TTH</th><th class="num">8月目标</th><th class="num">目标差距</th><th>当前观念</th><th>目标观念</th><th>机会点</th><th>行动计划</th><th>所需支持</th>
  </tr></thead><tbody>${rows||emptyRows}</tbody></table>`;
}
/* ---------- 智能复盘建议 ---------- */
function buildAdvice(h,cu){
  const lm=hLM(h);
  const tips=[];
  const t=h.trend_series;
  const tN=t[t.length-1], tP=t[t.length-2], tP2=t[t.length-3];
  if(tP!=null&&tN!=null&&tP>tN&&tP2!=null&&tP2>tP) tips.push({k:"销量",s:`近两月连续下滑，优先定位下滑客户与渠道变化（${lm} ${fmt(tN)} vs 前月 ${fmt(tP)}）`});
  if((h.big_share??0)>60) tips.push({k:"销量",s:`重点客户贡献达 ${fmt(h.big_share)}%，销量集中风险高，需培养第二梯队客户`});
  if((h.net??0)>=0&&(h.active7??0)<=5) tips.push({k:"销量",s:"医院增长但活跃客户少，增长由少数客户驱动，持续性需关注"});
  const aN=h.abcd?.A||0,bN=h.abcd?.B||0,cN=h.abcd?.C||0,dN=h.abcd?.D||0;
  const total=aN+bN+cN+dN;
  if(aN<=2&&bN>=aN*2&&bN>=3) tips.push({k:"结构",s:`A类客户仅 ${aN} 人而B类 ${bN} 人，优先制定「B转A」名单，抓人均产出提升空间`});
  if(total&&(cN+dN)/total>0.5) tips.push({k:"结构",s:`C/D类客户占比 ${Math.round((cN+dN)/total*100)}%，偏高，需重新评估目标客户池`});
  if(h.tag_count&&(h.active7??0)<(h.tag_count??0)*0.5) tips.push({k:"结构",s:`标签客户 ${fmt(h.tag_count)} 人但活跃率仅 ${fmt(h.active_rate)}%，优先激活存量，不急于扩充名单`});
  const cNow=CONCEPTS.map(c=>cu.filter(x=>x.c_now===c).length);
  const none=cNow[0], ladder=cNow[1], manage=cNow[4]+cNow[5]+cNow[6];
  if(none>=3) tips.push({k:"观念",s:`「不管不治」客户 ${none} 人占比较高，先完成基础疾病认知与治疗观念建立`});
  if(ladder>=3&&cNow[2]<ladder) tips.push({k:"观念",s:`「阶梯治疗」客户 ${ladder} 人多于「止痛优选」，重点推动止痛优选升级`});
  if(manage>0){ const mTth=cu.filter(x=>["治痛管理","资深治痛管理","治痛管理大师"].includes(x.c_now)).reduce((a,x)=>a+(x.tth[lm]||0),0); const mN=cu.filter(x=>["治痛管理","资深治痛管理","治痛管理大师"].includes(x.c_now)).length; if(mTth&&mTth/mN<130) tips.push({k:"观念",s:"已达治痛管理层级但人均产出偏低，检查处方场景、患者识别及院内渠道"}); }
  if((h.access==="未准入"||!h.access)&&(h.tth[lm]||0)>=100) tips.push({k:"准入",s:`未准入但${lm}已有 ${fmt(h.tth[lm])} 盒销量，作为准入推进重点医院`});
  if(h.access&&h.access!=="未准入"&&(h.net??0)<0) tips.push({k:"准入",s:"已准入但销量持续下滑，问题可能不在准入，转向客户覆盖与处方转化"});
  if(h.channel&&h.channel!=="无限制") tips.push({k:"准入",s:`院内渠道受限：${h.channel}，单独跟进渠道开放，避免误判为DM执行问题`});
  const box=document.getElementById("advice-box");
  if(!tips.length){ box.innerHTML=`<h4>💡 智能复盘建议</h4><ol><li>本医院当前未触发显著风险规则；建议按复盘五问过一遍：结果→来源→基础→转化→行动。</li></ol>`; return; }
  box.innerHTML=`<h4>💡 智能复盘建议（${Math.min(tips.length,5)}/5 条 · 自动生成）</h4><ol>`+
    tips.slice(0,5).map(t=>`<li><b>【${t.k}】</b>${t.s}</li>`).join("")+`</ol>`;
}

"""
# v4：重点医院概览改为内嵌独立复盘看板（hospital_overview.html，自包含 HTML），
# 避免与主脚本共享全局作用域（const charts / function fmt 等重名会报错），
# 同时保留主看板单文件入口：点击「重点医院概览」即加载该页。
html = html[:i3] + "/* 重点医院概览已通过 iframe 内嵌 hospital_overview.html，本段不再注入医院 JS */" + html[j3:]

# ---------- 7) 导出CSV hospital 分支补 8月TTH 列 ----------
_OLD_HEAD = '"6月TTH","7月TTH","当前观念","目标观念","机会点"];'
_NEW_HEAD = '"6月TTH","7月TTH","8月TTH","当前观念","目标观念","机会点"];'
html = html.replace(_OLD_HEAD, _NEW_HEAD)
_OLD_ROW = 'c.tth["6月"]||"",c.tth["7月"]||"",c.c_now'
_NEW_ROW = 'c.tth["6月"]||"",c.tth["7月"]||"",c.tth["8月"]||"",c.c_now'
html = html.replace(_OLD_ROW, _NEW_ROW)

# ---------- 6) 写出 ----------
import os
os.makedirs(os.path.dirname(OUT), exist_ok=True)
io.open(OUT, "w", encoding="utf-8").write(html)
print("written:", OUT, len(html), "chars")
