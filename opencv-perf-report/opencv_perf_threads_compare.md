# OpenCV 4.12.0 perf：单线程 vs 16 线程（带 opencv_extra 数据）

- 生成时间：2026-11-26 09:41:52
- 二进制：`D:\project\cppproject\opencv-build\bin\opencv_perf_*.exe`（MinGW GCC 14.2 / Release / OpenMP 后端）
- 数据：`D:\project\cppproject\opencv_extra\opencv_extra-4.x\testdata`（8,237 个文件 / 0.6 GB）
- 两轮唯一差异：`--perf_threads=1` 与 `--perf_threads=16`；其余环境完全一致（`OPENCV_OPENCL_RUNTIME=disabled`、`OPENCV_FOR_OPENMP_DYNAMIC_DISABLE=1`、空 `OPENCV_TEST_DATA_PATH` 已替换为真实数据）
- 配对用例：18879（两轮都产出 PERFSTAT 的用例；另有 1790 个用例中位数为 0.00ms，低于计时精度，已剔除）
- `speedup = median(t=1) / median(t=16)`，>1 表示 16 线程更快；每例采样 ≥10 次取中位数

## 一、各模块汇总（按用例统计）

| 模块 | 配对用例 | 几何平均加速 | 中位加速 | ≥1.5x 用例 | <0.9x 用例 |
|---|---|---|---|---|---|
| dnn | 977 | 1.75x | 1.93x | 563 | 221 |
| objdetect | 154 | 1.65x | 1.08x | 67 | 17 |
| imgproc | 5324 | 1.48x | 1.00x | 1568 | 436 |
| features2d | 233 | 1.47x | 1.00x | 50 | 0 |
| video | 201 | 1.28x | 1.34x | 66 | 40 |
| photo | 13 | 1.19x | 1.02x | 3 | 0 |
| calib3d | 117 | 1.15x | 1.00x | 19 | 8 |
| stitching | 91 | 1.14x | 1.01x | 12 | 1 |
| core | 5268 | 1.03x | 1.00x | 166 | 252 |
| gapi | 6389 | 1.03x | 1.00x | 353 | 597 |
| imgcodecs | 107 | 1.01x | 1.01x | 0 | 0 |
| videoio | 5 | 0.99x | 1.00x | 0 | 0 |

## 二、说明：为什么没给“整轮耗时”对比

perf 框架默认策略会按稳定性自动停采样（`stddev ≤ 3% 均值` 或最多 100 次）：
16 线程的抖动通常略大，于是同一用例可能跑 100 次采样，而单线程 12 次就停了。
这会让“整轮墙钟时间”失真（例如 features2d 16 线程反而更久，但每用例中位数其实更快），
所以本报告只比较**每用例中位数**，整轮耗时见 xlsx 的 `WallTime` sheet（仅供参考）。
若需要严格的墙钟对比，可两轮都加 `--perf_force_samples=10` 固定采样次数重跑。

## 三、加速最明显的 30 个用例

| 模块 | 用例 | 1线程(ms) | 16线程(ms) | 加速比 |
|---|---|---|---|---|
| core | `Size_MatType_ROp_reduceC.reduceC/34` | 3.09 | 0.18 | 17.17x |
| core | `OCL_LUTFixture_LUT.LUT/13` | 3.19 | 0.20 | 15.95x |
| core | `Size_MatType_ROp_reduceC.reduceC/31` | 2.63 | 0.17 | 15.47x |
| core | `Size_MatType_ROp_reduceC.reduceC/30` | 2.60 | 0.17 | 15.29x |
| imgproc | `TestRemap_remap.remap/172` | 2.92 | 0.20 | 14.60x |
| features2d | `Norm_CrossCheck_batchDistance_32F.batchDistance_32F/0` | 33.39 | 2.29 | 14.58x |
| features2d | `Norm_CrossCheck_batchDistance_32F.batchDistance_32F/1` | 66.92 | 4.63 | 14.45x |
| imgproc | `OCL_ResizeFixture_Resize.Resize/53` | 2.90 | 0.21 | 13.81x |
| dnn | `Layer_Softmax.softmax_3d/6` | 117.01 | 8.55 | 13.69x |
| imgproc | `OCL_ResizeFixture_Resize.Resize/55` | 4.24 | 0.31 | 13.68x |
| features2d | `Source_CrossCheck_batchDistance_L2.batchDistance_L2/1` | 93.80 | 6.87 | 13.65x |
| features2d | `Source_CrossCheck_batchDistance_L2.batchDistance_L2/0` | 46.73 | 3.44 | 13.58x |
| features2d | `Source_CrossCheck_batchDistance_L2.batchDistance_L2/2` | 12.99 | 0.96 | 13.53x |
| features2d | `Norm_Destination_CrossCheck_batchDistance_8U.batchDistance_8U/3` | 89.79 | 6.64 | 13.52x |
| features2d | `Norm_CrossCheck_batchDistance_32F.batchDistance_32F/3` | 26.12 | 1.95 | 13.39x |
| features2d | `Norm_Destination_CrossCheck_batchDistance_8U.batchDistance_8U/7` | 90.64 | 6.89 | 13.16x |
| features2d | `Norm_Destination_CrossCheck_batchDistance_8U.batchDistance_8U/6` | 44.99 | 3.42 | 13.15x |
| imgproc | `MatInfo_Size_Scale_NN_ResizeNNExact.ResizeNNExact/17` | 2.87 | 0.22 | 13.05x |
| features2d | `Norm_Destination_CrossCheck_batchDistance_8U.batchDistance_8U/2` | 44.71 | 3.43 | 13.03x |
| dnn | `Layer_GroupNorm.GroupNorm/0` | 14.00 | 1.08 | 12.96x |
| imgproc | `TestRemap_remap.remap/124` | 3.50 | 0.27 | 12.96x |
| core | `OCL_ReduceAccFixture_Reduce.Reduce/45` | 16.28 | 1.27 | 12.82x |
| core | `OCL_ReduceAccFixture_Reduce.Reduce/46` | 16.28 | 1.27 | 12.82x |
| imgproc | `TestRemap_remap.remap/174` | 2.82 | 0.22 | 12.82x |
| core | `OCL_ReduceAccFixture_Reduce.Reduce/47` | 16.23 | 1.27 | 12.78x |
| core | `OCL_ReduceMinMaxFixture_Reduce.Reduce/27` | 13.02 | 1.02 | 12.76x |
| imgproc | `Size_MatType_pyrDown.pyrDown/7` | 2.68 | 0.21 | 12.76x |
| core | `OCL_ReduceMinMaxFixture_Reduce.Reduce/26` | 13.06 | 1.03 | 12.68x |
| imgproc | `OCL_CvtColorFixture_CvtColor.CvtColor/87` | 9.00 | 0.71 | 12.68x |
| imgproc | `OCL_CvtColorFixture_CvtColor.CvtColor/88` | 8.33 | 0.66 | 12.62x |

## 四、16 线程反而更慢的 20 个用例

| 模块 | 用例 | 1线程(ms) | 16线程(ms) | 加速比 |
|---|---|---|---|---|
| core | `KMeans.single_iter/1` | 0.09 | 2.91 | 0.03x |
| core | `KMeans.good/1` | 0.11 | 3.35 | 0.03x |
| imgproc | `Size_MatType_buildPyramid.buildPyramid/26` | 0.01 | 0.27 | 0.04x |
| imgproc | `Size_MatType_buildPyramid.buildPyramid/18` | 0.01 | 0.27 | 0.04x |
| imgproc | `Size_MatType_buildPyramid.buildPyramid/25` | 0.01 | 0.27 | 0.04x |
| imgproc | `Size_MatType_buildPyramid.buildPyramid/28` | 0.01 | 0.26 | 0.04x |
| imgproc | `Size_MatType_buildPyramid.buildPyramid/29` | 0.01 | 0.26 | 0.04x |
| dnn | `MatMul.innerproduct/6` | 0.05 | 0.89 | 0.06x |
| dnn | `MatMul.innerproduct/7` | 0.05 | 0.89 | 0.06x |
| core | `KMeans.single_iter/11` | 4.44 | 77.46 | 0.06x |
| dnn | `MatMul.innerproduct/2` | 0.04 | 0.67 | 0.06x |
| core | `KMeans.single_iter/2` | 0.17 | 2.84 | 0.06x |
| dnn | `MatMul.innerproduct/3` | 0.04 | 0.66 | 0.06x |
| core | `KMeans.single_iter/4` | 0.36 | 5.93 | 0.06x |
| core | `KMeans.good/2` | 0.21 | 3.40 | 0.06x |
| core | `KMeans.single_iter/9` | 1.64 | 24.67 | 0.07x |
| core | `KMeans.single_iter/5` | 0.40 | 5.95 | 0.07x |
| core | `KMeans.single_iter/7` | 0.83 | 12.26 | 0.07x |
| gapi | `BuildOptFlowPyramidPerfTestCPU/BuildOptFlowPyramidPerfTest.TestPerformance/15` | 0.04 | 0.59 | 0.07x |
| gapi | `BuildOptFlowPyramidPerfTestCPU/BuildOptFlowPyramidPerfTest.TestPerformance/14` | 0.04 | 0.58 | 0.07x |

## 五、读法说明

1. 表中 `OCL_*` 用例名容易误导：本次 `OPENCV_OPENCL_RUNTIME=disabled`，它们实际跑的是 UMat 的 CPU 回退路径。
2. 中位加速 = 1.00x 不代表线程无效：该模块超过一半的用例是小尺寸/微秒级操作，并行调度开销吃掉收益（见第四节的反例）。
3. 大图/大数据量的算子加速明显：reduce、remap、resize、LUT、batchDistance、DNN softmax 都能到 12～17x。
4. `core` 的 `Gemm`/`dft` 在 640×640 这类尺寸几乎没有加速（1.0～1.1x），说明这两条路径在该尺寸下没走并行实现。
5. 每模块的完整用例级数据见 `AllTests` sheet / `opencv_perf_threads_compare.csv`。
