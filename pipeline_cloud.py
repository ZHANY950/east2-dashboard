# -*- coding: utf-8 -*-
"""东二区数据看板 — 云端版管线（GitHub Actions 运行，仓库根目录执行）

输入（全部来自仓库内，无需 Mac、无需腾讯文档票据）:
  sources/   数据快照目录
    ├── tth_q3.csv / mjq_data.csv / dm_daily_part1.csv / dm_daily_part2.csv   腾讯文档缓存快照
    ├── p303_raw.csv / p303_style.json                                         303 项目缓存
    ├── wps_244.json                                                           WPS 团队跟进缓存
    ├── dashboard_data.json                                                    医院底表缓存（大客户名单继承）
    ├── dzdk/word/media/image*.png                                             先锋图默认图
    ├── 【月表】患者画像每日跟进*.xlsx                                          ← 用户上传新版即触发更新
    └── TOPCORE医院DDD*.xlsx                                                   ← 用户上传新版即触发更新
  pipeline/   extract_dashboard / extract_v2 / build_v2 / build_web + dashboard.html 模板
  vendor/     chart.umd.min.js + chartjs-plugin-datalabels.min.js（内联用）

输出:
  index.html + data.js（commit 回仓库 main → GitHub Pages 自动生效，网页版点「🔄 刷新数据」即拉到最新）

用法: cd <repo根> && python3 pipeline_cloud.py
"""
import os
import shutil
import subprocess
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(ROOT, "sources")
BUILD = "/tmp/east2_build"
PY = sys.executable

env = dict(os.environ)
env.update({
    "EAST2_SRC": SRC,                                     # 中间缓存/输出都走 sources/
    "EAST2_YB_DIR": SRC,                                  # 月表在 sources/ 根
    "EAST2_DDD_DIR": SRC,                                 # DDD 名单在 sources/ 根
    "EAST2_DZDK": os.path.join(SRC, "dzdk"),              # 先锋图
    "EAST2_TMPL": os.path.join(ROOT, "pipeline", "dashboard.html"),
    "EAST2_OUT": os.path.join(BUILD, "dashboard.html"),   # 本地版产物（中间产物）
    "EAST2_LIB_DIR": os.path.join(ROOT, "vendor"),        # Chart.js 库
})


def run(label, *cmd):
    print(f"\n===== {label} =====", flush=True)
    r = subprocess.run(cmd, env=env, cwd=ROOT)
    if r.returncode != 0:
        sys.exit(f"[FAIL] {label} 退出码 {r.returncode}")


def main():
    # 校验关键输入
    required = ["tth_q3.csv", "mjq_data.csv", "dm_daily_part1.csv", "dm_daily_part2.csv",
                "p303_raw.csv", "p303_style.json", "wps_244.json", "dashboard_data.json"]
    missing = [f for f in required if not os.path.isfile(os.path.join(SRC, f))]
    if missing:
        sys.exit(f"[FAIL] sources/ 缺少缓存文件: {missing}")
    if not os.path.isfile(env["EAST2_TMPL"]):
        sys.exit(f"[FAIL] 缺少模板 {env['EAST2_TMPL']}")

    os.makedirs(BUILD, exist_ok=True)

    # 四步管线（与本地一致，只是输入目录不同）
    run("① extract_dashboard（医院底表）", PY, os.path.join(ROOT, "pipeline", "extract_dashboard.py"))
    run("② extract_v2（数据提取）", PY, os.path.join(ROOT, "pipeline", "extract_v2.py"))
    run("③ build_v2（本地看板构建）", PY, os.path.join(ROOT, "pipeline", "build_v2.py"))
    run("④ build_web（网页版构建）", PY, os.path.join(ROOT, "pipeline", "build_web.py"),
        env["EAST2_OUT"], os.path.join(BUILD, "index.html"))
    # build_web 产物: index.html + index_data.js → 拷为仓库根 index.html + data.js
    shutil.copy(os.path.join(BUILD, "index.html"), os.path.join(ROOT, "index.html"))
    shutil.copy(os.path.join(BUILD, "index_data.js"), os.path.join(ROOT, "data.js"))
    print("\n✅ 云端构建完成: index.html + data.js 已生成，待 commit 推送")


if __name__ == "__main__":
    main()
