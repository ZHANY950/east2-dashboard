# -*- coding: utf-8 -*-
"""构建重点医院概览单文件HTML：内联 Chart.js + hosp_overview.json 数据"""
import os, json
HERE = os.path.dirname(os.path.abspath(__file__))
TPL = os.path.join(HERE, "hospital_overview.template.html")
DATA = os.path.join(HERE, "hosp_overview.json")
CHART = os.path.join(HERE, "vendor", "chart.umd.min.js")
OUT = os.path.join(HERE, "hospital_overview.html")

chartjs = open(CHART, encoding="utf-8").read()
data = json.load(open(DATA, encoding="utf-8"))
data_js = "window.__HO__ = " + json.dumps(data, ensure_ascii=False) + ";"

tpl = open(TPL, encoding="utf-8").read()
assert "/*__CHARTJS__*/" in tpl and "/*__DATA__*/" in tpl, "模板占位符缺失"
html = tpl.replace("/*__CHARTJS__*/", chartjs).replace("/*__DATA__*/", data_js)

with open(OUT, "w", encoding="utf-8") as f:
    f.write(html)
print("✅ 构建完成:", OUT)
print("   大小:", round(os.path.getsize(OUT)/1024), "KB  (Chart.js", round(len(chartjs)/1024), "KB + 数据", round(len(data_js)/1024), "KB)")
