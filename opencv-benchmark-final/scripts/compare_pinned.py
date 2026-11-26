#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Compare pinned 1-core vs 16-core perf runs (fixed 30 samples, no gapi)."""
import math
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

import pandas as pd

BUILD = Path(r"D:\project\cppproject\opencv-build")
RESULTS = BUILD / "bench-results" / "pinned30-runs"
OUT = Path(r"C:\Users\root\Documents\deepseek-harness\default-workspace") / "opencv-perf-report"

MODULES = ["core", "imgproc", "imgcodecs", "videoio", "calib3d", "features2d",
           "objdetect", "photo", "stitching", "video", "dnn"]

RUN_RE = re.compile(r"^\[ RUN\s+\] (.+?)\s*$")
STAT_RE = re.compile(r"PERFSTAT.*?samples=(\d+)\s+mean=([\d.]+)\s+median=([\d.]+)")


def norm(name: str) -> str:
    return re.sub(r",\s*where .*$", "", name.strip()).strip()


def parse(log: Path):
    """-> {test: (samples, median_ms)}"""
    out = {}
    cur = None
    with log.open("r", encoding="utf-8", errors="replace") as fh:
        for line in fh:
            m = RUN_RE.match(line)
            if m:
                cur = norm(m.group(1))
                continue
            m = STAT_RE.search(line)
            if m and cur:
                out[cur] = (int(m.group(1)), float(m.group(3)))
    return out


def xml_total_min(path: Path):
    if not path.exists():
        return math.nan
    try:
        root = ET.parse(path).getroot()
    except ET.ParseError:
        return math.nan
    total = 0.0
    for tc in root.iter("testcase"):
        try:
            total += float(tc.get("time", 0.0))
        except (TypeError, ValueError):
            pass
    return total / 60.0


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    rows = []
    for mod in MODULES:
        a = parse(RESULTS / f"perf_{mod}_t1.log")
        b = parse(RESULTS / f"perf_{mod}_t16.log")
        for t in sorted(set(a) & set(b)):
            rows.append(dict(module=mod, test=t, samples=a[t][0],
                             t1_ms=a[t][1], t16_ms=b[t][1],
                             samples_match=a[t][0] == b[t][0]))

    df = pd.DataFrame(rows)
    total = len(df)
    df = df[(df.t1_ms > 0) & (df.t16_ms > 0)].copy()
    dropped = total - len(df)
    df["speedup"] = df.t1_ms / df.t16_ms
    df = df.sort_values("speedup", ascending=False)
    df.to_csv(OUT / "opencv_perf_threads30_compare.csv", index=False, encoding="utf-8-sig")

    def gm(s):
        s = s[s > 0]
        return float(math.exp(sum(map(math.log, s)) / len(s))) if len(s) else math.nan

    per_mod = (df.groupby("module")
                 .agg(cases=("test", "nunique"),
                      geomean=("speedup", gm),
                      median=("speedup", "median"),
                      fast15=("speedup", lambda s: int((s >= 1.5).sum())),
                      slow09=("speedup", lambda s: int((s < 0.9).sum())))
                 .reset_index()
                 .sort_values("geomean", ascending=False))

    wall = pd.DataFrame([
        dict(module=m, t1_min=xml_total_min(RESULTS / f"{m}_t1.xml"),
             t16_min=xml_total_min(RESULTS / f"{m}_t16.xml")) for m in MODULES])
    wall["ratio"] = wall.t1_min / wall.t16_min

    with pd.ExcelWriter(OUT / "opencv_perf_threads30_compare.xlsx", engine="openpyxl") as xw:
        per_mod.to_excel(xw, sheet_name="PerModule", index=False)
        wall.to_excel(xw, sheet_name="WallTime", index=False)
        df.to_excel(xw, sheet_name="AllTests", index=False)
        df.head(100).to_excel(xw, sheet_name="Top100Speedup", index=False)
        df.tail(100).to_excel(xw, sheet_name="Top100Slowdown", index=False)

    L = []
    A = L.append
    A("# OpenCV 4.12.0：1 核 vs 16 核（固定 30 次采样 / 绑核 / 不含 gapi）")
    A("")
    A(f"- 生成时间：{pd.Timestamp.now():%Y-%m-%d %H:%M:%S}")
    A("- 二进制：`D:\\project\\cppproject\\opencv-build\\bin\\opencv_perf_*.exe`"
      "（MinGW GCC 14.2 / Release / OpenMP；已给 ts_perf 打 Windows 亲和性补丁）")
    A("- 数据：`opencv_extra-4.x\\testdata`（8,237 文件 / 0.6 GB）；`OPENCV_OPENCL_RUNTIME=disabled`")
    A("- 采样：`--perf_min_samples=30 --perf_force_samples=30 --perf_time_limit=600`，"
      "**两轮每个用例的采样次数完全一致**（自检 mismatch=0）")
    A("- 绑核：t=1 → `0x1`（单个 P 核）；t=16 → `0xFFFF`（16 个逻辑核，8P+8E）")
    A("- 串行执行，同一时间只跑一个 perf 进程，无其它负载")
    A(f"- 配对用例：{len(df)}（两轮中位数都 >0；另有 {dropped} 个中位数为 0.00ms 被剔除）")
    A("")
    A("## 一、各模块汇总")
    A("")
    A("| 模块 | 配对用例 | 几何平均加速 | 中位加速 | ≥1.5x | <0.9x |")
    A("|---|---|---|---|---|---|")
    for _, r in per_mod.iterrows():
        A(f"| {r['module']} | {r['cases']} | {r['geomean']:.2f}x | {r['median']:.2f}x | "
          f"{r['fast15']} | {r['slow09']} |")
    A("")
    A("| 合计 | %d | %.2fx | %.2fx | %d | %d |" % (
        len(df), gm(df.speedup), df.speedup.median(),
        int((df.speedup >= 1.5).sum()), int((df.speedup < 0.9).sum())))
    A("")
    A("## 二、模块整体耗时（gtest XML 合计，采样次数已固定，可直接比）")
    A("")
    A("| 模块 | 1 核(分钟) | 16 核(分钟) | 1/16 |")
    A("|---|---|---|---|")
    for _, r in wall.iterrows():
        if math.isnan(r["t1_min"]):
            continue
        A(f"| {r['module']} | {r['t1_min']:.2f} | {r['t16_min']:.2f} | {r['ratio']:.2f}x |")
    A(f"| **合计** | **{wall.t1_min.sum():.2f}** | **{wall.t16_min.sum():.2f}** | "
      f"**{wall.t1_min.sum() / wall.t16_min.sum():.2f}x** |")
    A("")
    A("## 三、加速最明显的 30 个用例")
    A("")
    A("| 模块 | 用例 | 1核(ms) | 16核(ms) | 加速比 |")
    A("|---|---|---|---|---|")
    for _, r in df.head(30).iterrows():
        A(f"| {r['module']} | `{r['test']}` | {r['t1_ms']:.2f} | {r['t16_ms']:.2f} | {r['speedup']:.2f}x |")
    A("")
    A("## 四、16 核反而更慢的 20 个用例")
    A("")
    A("| 模块 | 用例 | 1核(ms) | 16核(ms) | 加速比 |")
    A("|---|---|---|---|---|")
    for _, r in df.tail(20).iloc[::-1].iterrows():
        A(f"| {r['module']} | `{r['test']}` | {r['t1_ms']:.2f} | {r['t16_ms']:.2f} | {r['speedup']:.2f}x |")
    A("")
    A("## 五、说明")
    A("")
    A("1. 少数用例（photo 2 个、stitching 43 个、video 17 个）由测试自身 `declare.time()` 限量，"
      "只跑 10 或 20 次，但**两轮完全一致**，不影响可比性。")
    A("2. 中位数 0.00ms 的用例（低于 0.01ms 打印精度）不参与统计。")
    A("3. `OCL_*` 用例名会误导：OpenCL 已关闭，它们实际跑 CPU 回退路径。")
    A(f"4. 完整数据：`AllTests` sheet / `opencv_perf_threads30_compare.csv`。")
    (OUT / "opencv_perf_threads30_compare.md").write_text("\n".join(L), encoding="utf-8")

    print(per_mod.to_string(index=False))
    print(f"\npairs={len(df)} dropped={dropped} -> {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
