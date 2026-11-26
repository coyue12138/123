# OpenCV 4.12.0：1 核 vs 16 核（固定 30 次采样 / 绑核 / 不含 gapi）

- 生成时间：2026-11-26 14:02:15
- 二进制：`D:\project\cppproject\opencv-build\bin\opencv_perf_*.exe`（MinGW GCC 14.2 / Release / OpenMP；已给 ts_perf 打 Windows 亲和性补丁）
- 数据：`opencv_extra-4.x\testdata`（8,237 文件 / 0.6 GB）；`OPENCV_OPENCL_RUNTIME=disabled`
- 采样：`--perf_min_samples=30 --perf_force_samples=30 --perf_time_limit=600`，**两轮每个用例的采样次数完全一致**（自检 mismatch=0）
- 绑核：t=1 → `0x1`（单个 P 核）；t=16 → `0xFFFF`（16 个逻辑核，8P+8E）
- 串行执行，同一时间只跑一个 perf 进程，无其它负载
- 配对用例：12493（两轮中位数都 >0；另有 1058 个中位数为 0.00ms 被剔除）

## 一、各模块汇总

| 模块 | 配对用例 | 几何平均加速 | 中位加速 | ≥1.5x | <0.9x |
|---|---|---|---|---|---|
| dnn | 977 | 1.74x | 2.00x | 577 | 216 |
| objdetect | 154 | 1.68x | 1.17x | 69 | 4 |
| features2d | 233 | 1.49x | 1.01x | 52 | 1 |
| imgproc | 5323 | 1.46x | 1.00x | 1550 | 364 |
| video | 201 | 1.31x | 1.39x | 76 | 38 |
| photo | 13 | 1.25x | 1.12x | 3 | 0 |
| calib3d | 116 | 1.16x | 1.00x | 20 | 11 |
| stitching | 91 | 1.16x | 1.02x | 11 | 1 |
| core | 5273 | 1.02x | 1.00x | 171 | 415 |
| imgcodecs | 107 | 1.02x | 1.02x | 0 | 0 |
| videoio | 5 | 0.98x | 1.00x | 0 | 0 |

| 合计 | 12493 | 1.26x | 1.00x | 2529 | 1050 |

## 二、模块整体耗时（gtest XML 合计，采样次数已固定，可直接比）

| 模块 | 1 核(分钟) | 16 核(分钟) | 1/16 |
|---|---|---|---|
| core | 14.76 | 14.61 | 1.01x |
| imgproc | 16.74 | 13.28 | 1.26x |
| imgcodecs | 3.48 | 3.42 | 1.02x |
| videoio | 0.00 | 0.00 | 0.33x |
| calib3d | 1.40 | 0.86 | 1.64x |
| features2d | 7.22 | 5.13 | 1.41x |
| objdetect | 2.74 | 1.18 | 2.33x |
| photo | 0.31 | 0.22 | 1.40x |
| stitching | 19.80 | 18.26 | 1.08x |
| video | 0.84 | 0.67 | 1.26x |
| dnn | 4.42 | 1.24 | 3.56x |
| **合计** | **71.72** | **58.87** | **1.22x** |

## 三、加速最明显的 30 个用例

| 模块 | 用例 | 1核(ms) | 16核(ms) | 加速比 |
|---|---|---|---|---|
| core | `Size_MatType_ROp_reduceC.reduceC/34` | 3.18 | 0.18 | 17.67x |
| core | `Size_MatType_ROp_reduceC.reduceC/30` | 2.74 | 0.18 | 15.22x |
| core | `Size_MatType_ROp_reduceC.reduceC/31` | 2.74 | 0.18 | 15.22x |
| features2d | `Source_CrossCheck_batchDistance_L2.batchDistance_L2/2` | 15.88 | 1.09 | 14.57x |
| dnn | `Layer_Softmax.softmax_3d/6` | 121.25 | 8.41 | 14.42x |
| features2d | `Norm_Destination_CrossCheck_batchDistance_8U.batchDistance_8U/2` | 44.78 | 3.22 | 13.91x |
| features2d | `Norm_Destination_CrossCheck_batchDistance_8U.batchDistance_8U/3` | 89.42 | 6.63 | 13.49x |
| dnn | `Gemm.innerproduct/1` | 81.35 | 6.07 | 13.40x |
| dnn | `Layer_GroupNorm.GroupNorm/0` | 14.21 | 1.09 | 13.04x |
| features2d | `Source_CrossCheck_batchDistance_L2.batchDistance_L2/1` | 94.34 | 7.28 | 12.96x |
| features2d | `Norm_CrossCheck_batchDistance_32F.batchDistance_32F/1` | 68.17 | 5.33 | 12.79x |
| features2d | `Norm_CrossCheck_batchDistance_32F.batchDistance_32F/0` | 34.06 | 2.67 | 12.76x |
| features2d | `Norm_CrossCheck_batchDistance_32F.batchDistance_32F/2` | 15.28 | 1.20 | 12.73x |
| features2d | `Source_CrossCheck_batchDistance_L2.batchDistance_L2/0` | 46.95 | 3.69 | 12.72x |
| features2d | `Norm_Destination_CrossCheck_batchDistance_8U.batchDistance_8U/6` | 45.44 | 3.59 | 12.66x |
| features2d | `Norm_Destination_CrossCheck_batchDistance_8U.batchDistance_8U/7` | 91.25 | 7.36 | 12.40x |
| features2d | `Norm_Destination_CrossCheck_batchDistance_8U.batchDistance_8U/5` | 37.40 | 3.06 | 12.22x |
| features2d | `Norm_Destination_CrossCheck_batchDistance_8U.batchDistance_8U/4` | 18.66 | 1.53 | 12.20x |
| core | `Size_MatType_ROp_reduceC.reduceC/19` | 1.40 | 0.12 | 11.67x |
| imgproc | `OCL_WarpAffineFixture_WarpAffine.WarpAffine/65` | 116.15 | 9.96 | 11.66x |
| imgproc | `TestRemap_remap.remap/170` | 2.98 | 0.26 | 11.46x |
| imgproc | `TestBilateralFilter_BilateralFilter.BilateralFilter/25` | 50.88 | 4.44 | 11.46x |
| core | `Size_MatType_ROp_reduceC.reduceC/43` | 4.43 | 0.39 | 11.36x |
| core | `Size_MatType_ROp_reduceC.reduceC/42` | 4.42 | 0.39 | 11.33x |
| imgproc | `OCL_WarpAffineFixture_WarpAffine.WarpAffine/46` | 18.97 | 1.68 | 11.29x |
| dnn | `Conv_3x3S1D1.conv/31` | 65.81 | 5.84 | 11.27x |
| imgproc | `TestRemap_remap.remap/168` | 2.81 | 0.25 | 11.24x |
| features2d | `OCL_BruteForceMatcherFixture_Match.Match/2` | 217.04 | 19.39 | 11.19x |
| imgproc | `OCL_WarpPerspectiveFixture_WarpPerspective.WarpPerspective/31` | 23.34 | 2.09 | 11.17x |
| core | `Size_MatType_ROp_reduceC.reduceC/37` | 5.69 | 0.51 | 11.16x |

## 四、16 核反而更慢的 20 个用例

| 模块 | 用例 | 1核(ms) | 16核(ms) | 加速比 |
|---|---|---|---|---|
| core | `KMeans.single_iter/1` | 0.09 | 2.78 | 0.03x |
| imgproc | `Size_MatType_buildPyramid.buildPyramid/18` | 0.01 | 0.29 | 0.03x |
| core | `KMeans.good/1` | 0.11 | 3.04 | 0.04x |
| imgproc | `Size_MatType_buildPyramid.buildPyramid/28` | 0.01 | 0.26 | 0.04x |
| imgproc | `Size_MatType_buildPyramid.buildPyramid/26` | 0.01 | 0.26 | 0.04x |
| imgproc | `Size_MatType_buildPyramid.buildPyramid/29` | 0.01 | 0.25 | 0.04x |
| imgproc | `Size_MatType_buildPyramid.buildPyramid/25` | 0.01 | 0.25 | 0.04x |
| core | `KMeans.single_iter/11` | 4.47 | 78.50 | 0.06x |
| core | `KMeans.single_iter/4` | 0.36 | 6.15 | 0.06x |
| dnn | `MatMul.innerproduct/6` | 0.05 | 0.85 | 0.06x |
| dnn | `MatMul.innerproduct/7` | 0.05 | 0.84 | 0.06x |
| dnn | `MatMul.innerproduct/2` | 0.04 | 0.67 | 0.06x |
| dnn | `MatMul.innerproduct/3` | 0.04 | 0.66 | 0.06x |
| core | `KMeans.single_iter/2` | 0.17 | 2.78 | 0.06x |
| core | `KMeans.single_iter/5` | 0.40 | 5.93 | 0.07x |
| core | `KMeans.single_iter/9` | 1.66 | 24.24 | 0.07x |
| core | `KMeans.single_iter/7` | 0.83 | 12.00 | 0.07x |
| core | `KMeans.good/2` | 0.21 | 3.01 | 0.07x |
| core | `KMeans.good/4` | 0.44 | 6.03 | 0.07x |
| dnn | `Conv_3x3S1D1.conv/258` | 0.01 | 0.13 | 0.08x |

## 五、说明

1. 少数用例（photo 2 个、stitching 43 个、video 17 个）由测试自身 `declare.time()` 限量，只跑 10 或 20 次，但**两轮完全一致**，不影响可比性。
2. 中位数 0.00ms 的用例（低于 0.01ms 打印精度）不参与统计。
3. `OCL_*` 用例名会误导：OpenCL 已关闭，它们实际跑 CPU 回退路径。
4. 完整数据：`AllTests` sheet / `opencv_perf_threads30_compare.csv`。