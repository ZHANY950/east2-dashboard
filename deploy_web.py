# -*- coding: utf-8 -*-
"""东二区数据看板 — 一键部署网页版到 GitHub Pages

流程:
  1. 运行四步数据管线（可用 --skip-build 跳过，直接用最近一次本地构建产物）
  2. build_web.py 生成网页版 HTML（内联 Chart.js + 密码门 + 移除本地刷新按钮）
  3. git 推送到 GitHub 仓库 ZHANY950/east2-dashboard（走本机代理 127.0.0.1:7897）
  4. 首次部署时自动开启 GitHub Pages

发布地址: https://zhany950.github.io/east2-dashboard/
微信 / 手机浏览器 / 电脑浏览器均可打开；访问密码见 build_web.py 的 WEB_PASSWORD。

用法:
  python3 deploy_web.py              # 全流程（重新抓数据+构建+发布）
  python3 deploy_web.py --skip-build # 跳过数据管线，直接发布最近构建
  python3 deploy_web.py --auto       # 定时任务模式（launchd）：经本地刷新服务刷新，
                                      # 数据实质无变化时不推送；服务掉线时自动用票据缓存拉起
"""
import datetime
import json
import os
import re
import subprocess
import sys
import time
import urllib.request

PY = "/Users/zhangyun/.workbuddy/binaries/python/envs/default/bin/python3"
WS = "/Users/zhangyun/Desktop/workbuddy/2026-08-26-18-32-05"
REPO = "https://github.com/ZHANY950/east2-dashboard.git"
CLONE_DIR = "/tmp/east2_web_repo"
WEB_HTML = "/tmp/东二区数据看板_web.html"
WEB_DATA = "/tmp/东二区数据看板_web_data.js"
PAGE_URL = "https://zhany950.github.io/east2-dashboard/"
PROXY = "http://127.0.0.1:7897"  # 系统代理（github.com 直连不通）
LOCAL_REFRESH = "http://localhost:8787/api/refresh"
LOCAL_STATUS = "http://localhost:8787/api/status"

CDN_LIBS = [
    ("/tmp/chart.umd.min.js", "https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js"),
    ("/tmp/chartjs-plugin-datalabels.min.js", "https://cdn.jsdelivr.net/npm/chartjs-plugin-datalabels@2.2.0/dist/chartjs-plugin-datalabels.min.js"),
]


def sh(cmd, cwd=None, env=None):
    print("$", " ".join(cmd) if isinstance(cmd, list) else cmd)
    p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, env=env)
    if p.stdout.strip():
        print(p.stdout[-1500:])
    if p.returncode != 0:
        print(p.stderr[-1500:])
        raise SystemExit(f"[ERR] 命令失败(exit={p.returncode}): {' '.join(cmd) if isinstance(cmd, list) else cmd}")
    return p.stdout


def git(repo_dir, *args):
    """git 命令：强制走系统代理（外层 shell 的 env 代理端口可能失效）"""
    return sh(["git", "-c", f"http.proxy={PROXY}", "-c", f"https.proxy={PROXY}", *args], cwd=repo_dir)


def ensure_libs():
    """缓存 Chart.js 本地库（build_web.py 内联用）"""
    import urllib.request
    for path, url in CDN_LIBS:
        if not os.path.isfile(path) or os.path.getsize(path) < 5000:
            print(f"下载 {url}")
            opener = urllib.request.build_opener(urllib.request.ProxyHandler({"http": PROXY, "https": PROXY}))
            with opener.open(url, timeout=60) as r, open(path, "wb") as f:
                f.write(r.read())
            print(f"  -> {path} ({os.path.getsize(path)} bytes)")


def http_json(url, timeout=30):
    """GET 一个本地 JSON 接口，失败返回 None"""
    try:
        with urllib.request.urlopen(url, timeout=timeout) as r:
            return json.loads(r.read().decode("utf-8"))
    except Exception:
        return None


def ensure_refresh_server():
    """--auto 模式：刷新服务掉线时，用票据缓存拉起（launchd 环境无 WorkBuddy 注入的票据）"""
    if http_json(LOCAL_STATUS):
        return True
    print("[auto] 本地刷新服务未运行，尝试用票据缓存拉起 ...")
    env = dict(os.environ)
    try:
        for line in open(os.path.expanduser("~/.east2/tokens.env"), encoding="utf-8"):
            line = line.strip()
            if "=" in line and not line.startswith("#"):
                k, v = line.split("=", 1)
                env.setdefault(k, v)
    except FileNotFoundError:
        print("[auto] 无票据缓存（需先在 WorkBuddy 会话内跑一次刷新生成），本轮跳过")
        return False
    logf = open("/tmp/refresh_server.log", "ab")
    subprocess.Popen([PY, os.path.join(WS, "refresh_server.py")], cwd=WS,
                     env=env, stdout=logf, stderr=logf,
                     start_new_session=True, close_fds=True)
    for _ in range(10):
        time.sleep(1)
        if http_json(LOCAL_STATUS):
            print("[auto] 刷新服务已拉起")
            return True
    print("[auto] 拉起失败，本轮跳过")
    return False


def run_remote_refresh():
    """--auto 模式：经本地刷新服务的 HTTP 接口跑四步管线（该进程持有腾讯文档票据）"""
    print("[auto] 调用本地刷新服务 ...")
    req = urllib.request.Request(LOCAL_REFRESH, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=300) as r:
            res = json.loads(r.read().decode("utf-8"))
    except Exception as e:
        print(f"[auto] 刷新请求失败: {e}")
        return False
    if not res.get("ok"):
        print(f"[auto] 刷新管线失败: {res.get('error')}")
        for line in (res.get("log") or "").split("\n"):
            if line.startswith("——"):
                print(" ", line)
        return False
    print(f"[auto] 刷新成功: {res.get('at')} ({res.get('dur')}s)")
    return True


def data_fingerprint(text):
    """data.js 去掉 refreshed_at 时间戳后的指纹——用于判断数据是否有实质变化"""
    return re.sub(r'("refreshed_at"\s*:\s*")[^"]*(")', r"\1\2", text)


def sync_repo_files(clone_dir):
    """把最新数据快照 + 管线脚本同步进仓库（v4.0 云端构建的输入源）：
    - sources/：腾讯文档缓存 CSV、wps_244、先锋图、dashboard_data 缓存、最新月表、最新 DDD
    - pipeline/ + pipeline_cloud.py：最新管线脚本（云端 Actions 构建用）
    本机发布 → 同步快照 → 触发 Actions 云端构建（双保险，Mac 关机时云端仍可用快照+用户上传构建）"""
    import glob as _glob
    import shutil as _shutil
    src = os.path.join(clone_dir, "sources")
    os.makedirs(os.path.join(src, "dzdk", "word", "media"), exist_ok=True)
    os.makedirs(os.path.join(clone_dir, "pipeline"), exist_ok=True)
    # 1) 腾讯文档缓存 + WPS + 医院底表缓存
    for f in ["tth_q3.csv", "mjq_data.csv", "dm_daily_part1.csv", "dm_daily_part2.csv",
              "p303_raw.csv", "p303_style.json", "wps_244.json", "dashboard_data.json"]:
        p = os.path.join("/tmp", f)
        if os.path.isfile(p):
            _shutil.copy2(p, os.path.join(src, f))
    # 2) 先锋图默认图
    for idx in (4, 5):
        p = f"/tmp/dzdk/word/media/image{idx}.png"
        if os.path.isfile(p):
            _shutil.copy2(p, os.path.join(src, "dzdk", "word", "media", f"image{idx}.png"))
    # 3) 最新月表（删除旧版，只保留最新一份，避免仓库越积越大）
    for old in _glob.glob(os.path.join(src, "【月表】患者画像每日跟进*.xlsx")):
        os.remove(old)
    ybs = _glob.glob("/Users/zhangyun/Desktop/基础数据源/【月表】患者画像每日跟进*.xlsx")
    if not ybs:
        ybs = _glob.glob("/Users/zhangyun/Desktop/会议有效性ppt/【月表】患者画像每日跟进*.xlsx")
    if ybs:
        _shutil.copy2(sorted(ybs)[-1], src)
    # 4) 最新 DDD 名单
    for old in _glob.glob(os.path.join(src, "TOPCORE医院DDD*.xlsx")):
        os.remove(old)
    ddds = _glob.glob("/Users/zhangyun/Desktop/表格汇总/TOPCORE医院DDD*.xlsx")
    if ddds:
        _shutil.copy2(sorted(ddds)[-1], src)
    # 5) 管线脚本 + 模板 + 云端编排
    for f in ["extract_dashboard.py", "extract_v2.py", "build_v2.py", "build_web.py", "dashboard.html"]:
        _shutil.copy2(os.path.join(WS, f), os.path.join(clone_dir, "pipeline", f))
    _shutil.copy2(os.path.join(WS, "pipeline_cloud.py"), os.path.join(clone_dir, "pipeline_cloud.py"))
    # 6) 重点医院概览脚本 + 模板 + Chart.js 库
    for f in ["extract_hosp_overview.py", "build_hosp_overview.py", "hospital_overview.template.html"]:
        if os.path.isfile(os.path.join(WS, f)):
            _shutil.copy2(os.path.join(WS, f), os.path.join(clone_dir, f))
    vend = os.path.join(WS, "vendor", "chart.umd.min.js")
    if os.path.isfile(vend):
        os.makedirs(os.path.join(clone_dir, "vendor"), exist_ok=True)
        _shutil.copy2(vend, os.path.join(clone_dir, "vendor", "chart.umd.min.js"))
    print("[sync] sources/ 快照与 pipeline/ 脚本已同步")


def _build_hosp_overview(clone_dir):
    """用最新 TOPCORE医院DDD 重算重点医院概览页并拷贝进仓库（自包含 HTML）"""
    hosp_src = os.path.join(WS, "hospital_overview.html")
    ddd = _glob.glob("/Users/zhangyun/Desktop/表格汇总/TOPCORE医院DDD*.xlsx")
    if not ddd:
        print("[hosp] 未找到 TOPCORE医院DDD，跳过重点医院概览构建")
        return
    try:
        print("\n===== 重点医院概览：extract + build =====")
        sh([PY, os.path.join(WS, "extract_hosp_overview.py")])
        sh([PY, os.path.join(WS, "build_hosp_overview.py")])
        if os.path.isfile(hosp_src):
            _shutil.copy2(hosp_src, os.path.join(clone_dir, "hospital_overview.html"))
            print("[hosp] hospital_overview.html 已同步")
    except Exception as e:
        print("[hosp] 构建失败（不影响主看板）:", e)


def publish(auto=False):
    """构建网页版并推送 GitHub（auto=True 时数据无实质变化则跳过推送）"""
    # 1) 网页版构建
    ensure_libs()
    print("\n===== build_web.py =====")
    sh([PY, os.path.join(WS, "build_web.py")])

    # 2) git 推送
    print("\n===== git 部署 =====")
    os.system(f"rm -rf {CLONE_DIR}")
    p = subprocess.run(["git", "-c", f"http.proxy={PROXY}", "clone", "--depth", "1", REPO, CLONE_DIR],
                       capture_output=True, text=True)
    if p.returncode != 0:
        # 仓库为空（首次部署）→ 本地初始化
        print("clone 失败（首次部署，初始化本地仓库）")
        os.makedirs(CLONE_DIR, exist_ok=True)
        git(CLONE_DIR, "init", "-b", "main")
        git(CLONE_DIR, "remote", "add", "origin", REPO)

    dst = os.path.join(CLONE_DIR, "index.html")
    # --auto 智能推送：data.js 去掉时间戳后与线上无差异（数据源无更新）则本轮不推送，
    # 避免 GitHub 仓库每小时堆积一个「只有时间戳变了」的空 commit
    if auto:
        old_data = os.path.join(CLONE_DIR, "data.js")
        try:
            with open(old_data, encoding="utf-8") as f:
                old_fp = data_fingerprint(f.read())
            with open(WEB_DATA, encoding="utf-8") as f:
                new_fp = data_fingerprint(f.read())
            if old_fp == new_fp:
                print("[auto] 数据源无实质变化，本轮不推送")
                return False
            print("[auto] 检测到数据变化，执行推送 ...")
        except FileNotFoundError:
            print("[auto] 线上无 data.js（首次部署），执行推送 ...")
    with open(WEB_HTML, encoding="utf-8") as f:
        html = f.read()
    with open(dst, "w", encoding="utf-8") as f:
        f.write(html)
    # data.js（网页版刷新按钮重拉的数据文件，与 index.html 一起发布）
    dst_data = os.path.join(CLONE_DIR, "data.js")
    with open(WEB_DATA, encoding="utf-8") as f:
        datajs = f.read()
    with open(dst_data, "w", encoding="utf-8") as f:
        f.write(datajs)

    # 重点医院概览页：本地用最新 TOPCORE医院DDD 重算并拷贝（自包含 HTML，数据已内联）
    _build_hosp_overview(CLONE_DIR)

    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    sync_repo_files(CLONE_DIR)   # 同步云端快照（v4.0：触发 Actions 云端构建）
    git(CLONE_DIR, "add", "index.html", "data.js", "hospital_overview.html",
        "sources", "pipeline", "pipeline_cloud.py")
    # 无变化时 commit 会失败，先检查
    st = git(CLONE_DIR, "status", "--porcelain")
    if not st.strip():
        print("内容无变化，无需推送")
        return False
    git(CLONE_DIR, "commit", "-m", f"数据更新 {ts}")
    git(CLONE_DIR, "push", "-u", "origin", "main")
    print(f"推送完成: {ts}")

    # 3) 首次部署：开启 GitHub Pages
    import json
    pages_info = subprocess.run(["/Users/zhangyun/bin/gh", "api", "repos/ZHANY950/east2-dashboard/pages"],
                                capture_output=True, text=True)
    if pages_info.returncode != 0:
        print("开启 GitHub Pages ...")
        body = json.dumps({"source": {"branch": "main", "path": "/"}})
        subprocess.run(["/Users/zhangyun/bin/gh", "api", "-X", "POST",
                        "repos/ZHANY950/east2-dashboard/pages", "--input", "-"],
                       input=body, text=True, capture_output=True)
    print("✅ 网页版已发布（首次生效约需 1-2 分钟）: " + PAGE_URL)
    return True


def main():
    skip_build = "--skip-build" in sys.argv
    auto = "--auto" in sys.argv

    # 1) 数据管线
    if auto:
        # 定时任务模式：不直接跑管线（外部进程无腾讯文档票据），
        # 而是经本地刷新服务（常驻、持有票据）远程执行；服务掉线则先自愈拉起
        if not ensure_refresh_server():
            return
        if not run_remote_refresh():
            return
    elif not skip_build:
        for script in ["refresh_sources.py", "extract_dashboard.py", "extract_v2.py", "build_v2.py"]:
            print(f"\n===== {script} =====")
            sh([PY, script], cwd=WS)

    # 2) 构建并推送
    publish(auto=auto)

    if not auto:
        print(f"""
============================================================
✅ 网页版已发布（首次生效约需 1-2 分钟）

   访问地址: {PAGE_URL}
   访问密码: 见 build_web.py 的 WEB_PASSWORD（当前 0818）

   微信 / 手机浏览器直接打开上方链接即可；
   数据更新流程: 本地跑「部署网页版.command」一键重抓+构建+发布。
============================================================""")


if __name__ == "__main__":
    main()
