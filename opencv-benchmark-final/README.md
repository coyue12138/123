# OpenCV 4.12.0 Benchmark 汇总（最新一次：固定 30 次采样 + 绑核 + 不含 gapi）

## 这是什么

在 Windows 上用 MinGW-w64 GCC 14.2 自行编译 OpenCV 4.12.0（Release、`BUILD_PERF_TESTS=ON`），
跑 `opencv_perf_*.exe` 里自带的性能测试，比较 **1 核 vs 16 核**。

## 实验设置

| 项 | 值 |
|---|---|
| OpenCV | 4.12.0（源码 `D:\project\cppproject\opencv-4.12.0` 自编译） |
| 编译器 / 构建 | MinGW-w64 GCC 14.2.0 / Ninja / CMake 3.31.6 / Release |
| 并行后端 | OpenMP |
| 测试数据 | opencv_extra 4.x，8,237 文件 / 0.6 GB |
| 采样 | `--perf_min_samples=30 --perf_force_samples=30 --perf_time_limit=600`（每例 30 次） |
| 绑核 | t=1 → `0x1`；t=16 → `0xFFFF`（16 逻辑核，8P+8E） |
| OpenCL | 关闭（`OPENCV_OPENCL_RUNTIME=disabled`） |
| 模块 | 11 个，**不含 gapi**；串行执行 |
| 机器 | Intel Core Ultra 7 265（20 线程）/ 31.4 GB / Windows 11 26200 |

## 结果概览

- 配对用例：**12,493**（两轮中位数都 >0；另有 1,058 个 0.00ms 用例剔除）
- 全部用例几何平均加速：**1.26x**，中位 1.00x
- 整轮耗时：1 核 **71.7 分钟** → 16 核 **58.9 分钟**（1.22x）

| 模块 | 配对用例 | 几何平均加速 |
|---|---|---|
| dnn | 977 | 1.74x |
| objdetect | 154 | 1.68x |
| features2d | 233 | 1.49x |
| imgproc | 5323 | 1.46x |
| video | 201 | 1.31x |
| photo | 13 | 1.25x |
| calib3d | 116 | 1.16x |
| stitching | 91 | 1.16x |
| core | 5273 | 1.02x |
| imgcodecs | 107 | 1.02x |
| videoio | 5 | 0.98x |

## 文件说明

```
opencv-benchmark-final/
├─ README.md                      本文件
├─ report/
│  ├─ opencv_perf_all_in_one.xlsx  ★ 一个文件看全部（6 个 sheet）
│  ├─ opencv_perf_threads30_compare.md   对比报告（含结论、Top30、反例）
│  ├─ opencv_perf_threads30_compare.csv  12,493 条逐用例明细
│  ├─ opencv_perf_threads30_compare.xlsx 同上的 Excel 版
│  ├─ opencv_perf_threads30_by_suite.md  390 个算子的耗时汇总
│  └─ opencv_perf_threads30_by_suite.csv
├─ raw/                           22 个日志 + 22 个 gtest XML + MANIFEST.txt
├─ scripts/                       本次使用的解析/对比脚本
└─ history/                       之前两轮的报告（自适应采样 / 无数据全量）
```

## Excel 各 sheet

| sheet | 内容 |
|---|---|
| 1-模块汇总 | 每个模块的配对用例数、几何平均/中位加速 |
| 2-整轮耗时 | 每模块 1 核 vs 16 核的总耗时（采样次数已固定，可直接比） |
| 3-按算子 | 390 个测试套件的 1核/16核 中位、最小、最大 |
| 4-逐用例 | 12,493 条：模块/用例/采样数/1核ms/16核ms/加速比 |
| 5-加速Top100 / 6-变慢Top100 | 两端极值 |

## 怎么用原始日志

```powershell
# 查某个算子的每条参数记录
Select-String 'raw\perf_imgproc_t*.log' -Pattern 'PERFSTAT' | Select-Object -First 10

# 用官方脚本汇总某个 XML
D:\project\python\Python31011\python.exe `
  D:\project\cppproject\opencv-4.12.0\modules\ts\misc\perf_tests_timing.py raw\core_t16.xml
```

## 注意

1. 本次关闭了 IPP-ICV 与 FFmpeg，`resize`/`cvtColor` 等函数会比官方发行版慢，但两轮同二进制，比值不受影响。
2. 少数用例（photo 2、stitching 43、video 17）被测试自身的 `declare.time()` 限到 10/20 次采样，两轮一致。
3. `OCL_*` 用例关闭 OpenCL 后跑的是 CPU 回退路径，名字有误导性。
4. 8 个 `OCL_HoughLines` 失败用例，是关闭 OpenCL 导致，与本对比无关。
