# -*- coding: utf-8 -*-
"""东二区数据看板 — 网页版构建（GitHub Pages 发布用）

把本地构建产物「东二区数据看板.html」转换为可公开发布的网页版：
  1. Chart.js / datalabels 由 jsdelivr CDN 改为内联（大陆 & 微信内置浏览器对 jsdelivr 访问不稳定）
  2. 数据拆分：内嵌 const D={...} 抽出为独立 data.js（window.__DASH = {...}），
     页面改为引用 window.__DASH —— 这样「刷新数据」按钮可单独重拉 data.js 并原地重渲染
  3. 「🔄 刷新数据」按钮改为网页版逻辑 webRefresh()：fetch data.js（no-store 防缓存）
     → refreshed_at 相同提示已是最新；不同则原地更新 D 并重渲染两个页面
  4. 注入前端密码门（同「会议执行进度看板」模式，sessionStorage 记忆）

产物:
  OUT            网页版 index.html（引用 data.js?v=<refreshed_at>）
  OUT_DATA       data.js（window.__DASH = {...}）

用法: python3 build_web.py [源HTML路径] [输出HTML路径]
默认: 源=项目汇总/workbuddy/东二区数据看板.html  输出=/tmp/东二区数据看板_web.html
"""
import os
import re
import sys

# ===== 配置 =====
WEB_PASSWORD = os.environ.get("EAST2_WEB_PW", "0818")  # 网页版访问密码（与会议执行进度看板一致；修改后需重新部署）
SRC = sys.argv[1] if len(sys.argv) > 1 else "/Users/zhangyun/Desktop/项目汇总/workbuddy/东二区数据看板.html"
OUT = sys.argv[2] if len(sys.argv) > 2 else "/tmp/东二区数据看板_web.html"
OUT_DATA = OUT[:-5] + "_data.js" if OUT.endswith(".html") else OUT + "_data.js"

# Chart.js 库缓存目录（云端 Actions = 仓库 vendor/；本地默认 /tmp，由 deploy_web.py 自动下载）
_LIB_DIR = os.environ.get("EAST2_LIB_DIR", "/tmp")
CHART_LIB = os.path.join(_LIB_DIR, "chart.umd.min.js")                    # chart.js@4.4.1 umd
DL_LIB = os.path.join(_LIB_DIR, "chartjs-plugin-datalabels.min.js")       # chartjs-plugin-datalabels@2.2.0

CDN_TAGS = [
    '<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js"></script>',
    '<script src="https://cdn.jsdelivr.net/npm/chartjs-plugin-datalabels@2.2.0"></script>',
]

# 刷新按钮两行（build_v2.py 生成的固定标记）
BTN_BLOCK = (
    '          <button class="btn btn-refresh" id="btn-refresh" onclick="refreshData()" '
    'title="重新抓取腾讯文档数据源并更新全部模块">🔄 刷新数据</button>\n'
)
BTN_WEB = (
    '          <button class="btn btn-refresh" id="btn-refresh" onclick="webRefresh()" '
    'title="拉取服务器上最新发布的数据并刷新看板">🔄 刷新数据</button>\n'
)

GATE_CSS = """
<style id="web-gate-css">
/* ===== 网页版密码门 ===== */
#wg-mask{position:fixed;inset:0;z-index:99999;background:linear-gradient(160deg,#0f1e33,#16283e 55%,#0d1a2c);
display:flex;align-items:center;justify-content:center;font-family:-apple-system,"PingFang SC","Microsoft YaHei",sans-serif}
#wg-card{width:320px;background:#fff;border-radius:16px;padding:30px 28px 26px;box-shadow:0 18px 60px rgba(0,0,0,.45);text-align:center}
#wg-icon{width:52px;height:52px;margin:0 auto 14px;border-radius:14px;background:#eef4ff;display:flex;align-items:center;justify-content:center;font-size:26px}
#wg-card h2{margin:0 0 6px;font-size:17px;color:#16283e}
#wg-card p{margin:0 0 16px;font-size:12px;color:#8a99a9}
#wg-input{width:100%;box-sizing:border-box;padding:10px 12px;border:1px solid #d5dee8;border-radius:10px;
font-size:15px;text-align:center;letter-spacing:4px;outline:none}
#wg-input:focus{border-color:#3b82f6}
#wg-btn{width:100%;margin-top:12px;padding:10px 0;border:0;border-radius:10px;background:#2563eb;color:#fff;
font-size:14px;cursor:pointer}
#wg-btn:active{background:#1d4ed8}
#wg-err{min-height:18px;margin-top:10px;font-size:12px;color:#dc2626}
#wg-foot{margin-top:14px;font-size:11px;color:#b9c4d0}
</style>
"""

GATE_HTML = """
<div id="wg-mask" style="display:none">
  <div id="wg-card">
    <div id="wg-icon">🔐</div>
    <h2>东二区数据看板</h2>
    <p>请输入访问密码</p>
    <input id="wg-input" type="password" maxlength="20" placeholder="输入密码"
           onkeydown="if(event.key==='Enter')wgCheck()">
    <button id="wg-btn" onclick="wgCheck()">进入看板</button>
    <div id="wg-err"></div>
    <div id="wg-foot">仅限授权人员访问 · 请勿转发链接</div>
  </div>
</div>
<script id="web-gate-js">
(function(){
  var PW = "__WG_PW__";
  var mask = document.getElementById("wg-mask");
  if (!mask) return;
  // 每次新开会话都要验证；同一会话内刷新/跳转不再重复询问
  if (sessionStorage.getItem("east2_web_ok") === "1") return;
  mask.style.display = "flex";
  document.body.style.overflow = "hidden";
  setTimeout(function(){ var i = document.getElementById("wg-input"); if (i) i.focus(); }, 60);
})();
function wgCheck(){
  var v = (document.getElementById("wg-input").value || "").trim();
  var err = document.getElementById("wg-err");
  if (!v) { err.textContent = "请输入密码"; return; }
  if (v !== "__WG_PW__") { err.textContent = "密码错误，请重试"; return; }
  sessionStorage.setItem("east2_web_ok", "1");
  var mask = document.getElementById("wg-mask");
  mask.style.display = "none";
  document.body.style.overflow = "";
}
// 网页版：刷新按钮 → 重拉 data.js 并原地重渲染（无需整页刷新，密码记忆不丢失）
async function webRefresh(){
  var btn=document.getElementById("btn-refresh");
  if(btn){btn.classList.add("busy");btn.innerHTML='<span class="spin">🔄</span> 刷新中…';}
  try{
    var r=await fetch("data.js?t="+Date.now(),{cache:"no-store"});
    if(!r.ok) throw new Error("HTTP "+r.status);
    var txt=await r.text();
    var i=txt.indexOf("=");
    if(i<0) throw new Error("data.js 格式异常");
    var nd=JSON.parse(txt.slice(i+1).replace(/;\\s*$/,""));
    if(!nd||!nd.refreshed_at) throw new Error("数据字段缺失");
    if(nd.refreshed_at===D.refreshed_at){
      rfResetBtn();
      rfModal('<h4>✅ 已是最新数据</h4><p>最后更新：'+nd.refreshed_at+'</p>'+
              '<button class="rf-close" onclick="rfCloseModal()">知道了</button>');
      return;
    }
    /* 原地更新数据对象（const D 只改内容不改绑定），两个页面共用同一 D */
    Object.keys(D).forEach(function(k){delete D[k];});
    Object.assign(D,nd);
    fmtRefreshAt();
    applyRegionFilter();   /* 页面1：按当前筛选状态重渲染 */
    renderMod();           /* 页面1：当前打开的模块重渲染 */
    if(window._hfInit){try{renderHospTable();}catch(e){}}  /* 页面2：医院表重渲染 */
    rfResetBtn();
    rfModal('<h4>✅ 数据已更新</h4><p>已加载最新数据：'+D.refreshed_at+'</p>'+
            '<button class="rf-close" onclick="rfCloseModal()">知道了</button>');
  }catch(e){
    rfResetBtn();
    rfModal('<h4>⚠️ 刷新失败</h4><p>'+(e&&e.message?e.message:e)+'</p>'+
            '<p style="font-size:12px;color:#8a99a9">请检查网络后重试；新数据由管理员本地运行「部署网页版.command」发布。</p>'+
            '<button class="rf-close" onclick="rfCloseModal()">知道了</button>');
  }
}
function refreshData(){webRefresh();}  /* 兼容其他调用入口 */
</script>
"""


def read(p):
    with open(p, encoding="utf-8") as f:
        return f.read()


def main():
    html = read(SRC)

    # 1) 内联 Chart.js（CDN 在大陆/微信内不稳定）
    for tag, lib in zip(CDN_TAGS, [CHART_LIB, DL_LIB]):
        if tag not in html:
            raise SystemExit(f"[ERR] 未找到 CDN 标记: {tag}")
        if not os.path.isfile(lib):
            raise SystemExit(f"[ERR] 缺少本地库文件 {lib}，请先下载（见 deploy_web.py 缓存步骤）")
        html = html.replace(tag, "<script>\n" + read(lib) + "\n</script>", 1)

    # 2) 数据拆分：const D = {...}; 单行 → 独立 data.js + 页面引用
    lines = html.split("\n")
    idx = next((i for i, ln in enumerate(lines)
                if ln.startswith("const D = {") and ln.rstrip().endswith("};")), None)
    if idx is None:
        raise SystemExit("[ERR] 未找到 const D = {...} 数据行（build_v2.py 输出格式可能已变）")
    d_line = lines[idx].strip()
    d_json = d_line[len("const D = "):-1]  # 去掉前缀与结尾分号
    m = re.search(r'"refreshed_at":"([^"]*)"', d_json)
    ver = re.sub(r"\D", "", m.group(1)) if m else "1"  # 版本号=刷新时间数字
    with open(OUT_DATA, "w", encoding="utf-8") as f:
        f.write("window.__DASH = " + d_json + ";\n")
    lines[idx] = 'const D = window.__DASH || {refreshed_at:"(数据文件 data.js 未加载，请刷新页面重试)"};'
    html = "\n".join(lines)
    # 主 script 前插入 data.js 引用（v= 刷新时间，部署更新后浏览器自动弃用旧缓存）
    anchor = "const D = window.__DASH"
    pos = html.find("<script>\n" + anchor)
    if pos < 0:
        raise SystemExit("[ERR] 未找到主 script 锚点，无法插入 data.js 引用")
    html = html[:pos] + f'<script src="data.js?v={ver}"></script>\n' + html[pos:]

    # 3) 刷新按钮 → 网页版刷新逻辑（webRefresh：重拉 data.js 原地重渲染）
    if BTN_BLOCK in html:
        html = html.replace(BTN_BLOCK, BTN_WEB, 1)
    else:
        print("[WARN] 未找到刷新按钮标记（build_v2.py 输出格式可能已变），跳过按钮替换")

    # 4) 密码门（插在 </body> 前）
    gate = GATE_CSS + GATE_HTML.replace("__WG_PW__", WEB_PASSWORD)
    if "</body>" not in html:
        raise SystemExit("[ERR] HTML 中未找到 </body>")
    html = html.replace("</body>", gate + "\n</body>", 1)

    with open(OUT, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"OK 网页版构建: {OUT} ({len(html)} chars, 密码门已注入, Chart.js 已内联)")
    print(f"OK 数据文件: {OUT_DATA} ({os.path.getsize(OUT_DATA)} bytes, 版本 v={ver})")


if __name__ == "__main__":
    main()
