# OpenCV 4.12.0 自带 Benchmark（perf tests）运行报告

- 生成时间：2026-11-24 21:11:51
- 源码：`D:\project\cppproject\opencv-4.12.0`（OpenCV 4.12.0 官方源码）
- 构建目录：`D:\project\cppproject\opencv-build`（Ninja + MinGW-w64 GCC 14.2.0 + CMake 3.31.6，Release）
- 运行环境：Intel(R) Core(TM) Ultra 7 265 (20 cores / 20 threads, up to 5.3 GHz)；内存 31.4 GB；Lenovo 91BN000FCD；Windows 11 (10.0.26200), x64
- 共用例（声明）：**27322**；实际执行：**22782**；产出有效性能数据：**21210**；因缺 opencv_extra 数据跳过：1445；其它跳过：0；失败：0

## 一、结论速览

- 12 个模块的 `opencv_perf_*.exe` 全部编译成功并跑完（gapi 首次运行时 Intel iGPU 的 OpenCL 在 `CannyPerfTestGPU` 上触发 `CL_OUT_OF_RESOURCES` 崩溃，故 gapi 的 GPU 用例被排除后重跑；其余模块无崩溃）。
- **21210** 个用例给出了有效耗时统计（perf 框架默认策略：每例 ≥10 次采样、上限 3s，取中位数），**0** 个真实失败。
- **1445** 个用例需要 `opencv_extra` 测试数据（`cv/shared/lena.png`、DNN 模型等），因未下载数据被自动跳过；补齐数据后可直接重跑，无需重新编译。
- 全部原始数据在 `opencv_perf_results.xlsx` / `.csv`，可按模块、用例名筛选。

## 二、用例为什么没有全跑（27322 → 22782 → 21210）

- gtest 声明用例 **27322** 个（`--gtest_list_tests`）。
- 实际执行 **22782** 个：
  - gapi 的 `*GPU*`（OpenCL）用例 **3298** 个被 `--gtest_filter=-*GPU*` 排除（Intel iGPU 驱动在 `CannyPerfTestGPU` 上抛 `CL_OUT_OF_RESOURCES` 并崩溃）；
  - 其余 1242 个是 OpenCV 自带的 `DISABLED_` 用例，以及带 `verylong`、`mem_6gb` 标签的用例——perf 框架默认就不跑它们。
- 执行后产出有效数据 **21210** 个，缺数据跳过 1445 个，真实失败 0 个。

## 三、各模块汇总

| 模块 | 声明用例 | 实际执行 | 有效数据 | 缺数据跳过 | 失败 | 用例中位数(ms) | 最大中位数(ms) |
|---|---|---|---|---|---|---|---|
| core | 5813 | 5781 | 5781 | 0 | 0 | 0.230 | 129.0 |
| imgproc | 6920 | 5839 | 5390 | 449 | 0 | 0.220 | 74.4 |
| imgcodecs | 107 | 107 | 0 | 107 | 0 | - | - |
| videoio | 18 | 18 | 0 | 17 | 0 | - | - |
| calib3d | 125 | 121 | 106 | 15 | 0 | 0.240 | 338.2 |
| features2d | 233 | 233 | 29 | 204 | 0 | 2.600 | 26.8 |
| objdetect | 155 | 155 | 43 | 112 | 0 | 7.770 | 198.5 |
| photo | 15 | 13 | 0 | 13 | 0 | - | - |
| stitching | 91 | 91 | 32 | 59 | 0 | 1.140 | 14.8 |
| video | 247 | 231 | 26 | 205 | 0 | 23.565 | 102.6 |
| dnn | 3052 | 3051 | 2902 | 23 | 0 | 0.445 | 237.6 |
| gapi | 10546 | 7142 | 6901 | 241 | 0 | 0.100 | 125.2 |

## 四、最慢的 30 个用例

| 模块 | 用例 | 中位数(ms) | 最小(ms) | 采样数 |
|---|---|---|---|---|
| calib3d | `TestStereoCorrespSGBM_SGBM.SGBM/0` | 338.17 | 327.41 | 10 |
| calib3d | `TestStereoCorrespSGBM_SGBM.SGBM/2` | 299.14 | 291.74 | 10 |
| dnn | `Layer_FullyConnected.fc/34` | 237.61 | 226.56 | 10 |
| dnn | `Utils_blobFromImages.HWC_TO_NCHW/6` | 215.19 | 204.13 | 19 |
| objdetect | `Perf_Objdetect_Not_QRCode.detect/8` | 198.46 | 198.17 | 10 |
| calib3d | `TestStereoCorrespSGBM_SGBM.SGBM/5` | 172.21 | 166.80 | 14 |
| calib3d | `TestStereoCorrespSGBM_SGBM.SGBM/3` | 160.91 | 159.72 | 10 |
| dnn | `Layer_FullyConnected.fc/28` | 138.01 | 132.64 | 13 |
| core | `OCL_BufferPoolFixture_BufferPool_UMatIntegral10.BufferPool_UMatIntegral10/0` | 129.04 | 125.07 | 10 |
| gapi | `Benchmark/SobelEdgeDetector.OpenCV/4` | 125.18 | 118.82 | 100 |
| dnn | `Layer_FullyConnected.fc/31` | 122.14 | 120.29 | 10 |
| core | `KMeans.with_duplicates/11` | 114.18 | 108.61 | 25 |
| objdetect | `Perf_Objdetect_Not_QRCode.detect/11` | 108.50 | 107.06 | 10 |
| objdetect | `Perf_Objdetect_Not_QRCode.decode/7` | 105.87 | 104.30 | 10 |
| objdetect | `Perf_Objdetect_Not_QRCode.decode/3` | 105.55 | 104.76 | 10 |
| video | `OCL_DenseOpticalFlow_DIS_perf.perf/8` | 102.57 | 97.18 | 13 |
| objdetect | `Perf_Objdetect_Not_QRCode.decode/11` | 102.33 | 100.75 | 10 |
| core | `KMeans.good/11` | 101.40 | 99.38 | 13 |
| video | `DenseOpticalFlow_DIS_perf.perf/8` | 95.67 | 89.46 | 10 |
| core | `KMeans.single_iter/11` | 95.01 | 92.54 | 10 |
| core | `Size_MatType_FlagsType_NzeroRows_dft.dft/167` | 93.78 | 83.96 | 76 |
| core | `Size_MatType_FlagsType_NzeroRows_dft.dft/159` | 93.29 | 83.64 | 100 |
| dnn | `Layer_FullyConnected.fc/33` | 91.59 | 81.56 | 100 |
| core | `Size_MatType_FlagsType_NzeroRows_dft.dft/157` | 91.40 | 87.75 | 10 |
| objdetect | `Perf_Objdetect_Not_QRCode.detect/7` | 91.05 | 90.28 | 10 |
| objdetect | `Perf_Objdetect_Not_QRCode.detect/3` | 90.77 | 89.96 | 10 |
| dnn | `Layer_FullyConnected.fc/22` | 85.69 | 81.36 | 11 |
| core | `Size_MatType_FlagsType_NzeroRows_dft.dft/161` | 85.00 | 83.81 | 13 |
| core | `Size_MatType_FlagsType_NzeroRows_dft.dft/163` | 83.99 | 82.81 | 13 |
| core | `OCL_TransformFixture_Transform.Transform/27` | 82.23 | 80.49 | 10 |

## 五、构建与运行方式（可复现）

```powershell
# 1) 配置（关键：BUILD_PERF_TESTS=ON 才会生成 opencv_perf_*）
cmake -S D:\project\cppproject\opencv-4.12.0 -B D:\project\cppproject\opencv-build -G Ninja `
  -DCMAKE_BUILD_TYPE=Release `
  -DCMAKE_C_COMPILER=D:\project\cppproject\tools\mingw64\bin\gcc.exe `
  -DCMAKE_CXX_COMPILER=D:\project\cppproject\tools\mingw64\bin\g++.exe `
  -DBUILD_PERF_TESTS=ON -DBUILD_TESTS=OFF -DBUILD_EXAMPLES=OFF `
  -DBUILD_JAVA=OFF -DBUILD_opencv_python3=OFF -DBUILD_opencv_js=OFF `
  -DWITH_IPP=OFF -DWITH_FFMPEG=OFF -DENABLE_PRECOMPILED_HEADERS=OFF
# 2) 编译（20 线程，约 4 分钟）
ninja -C D:\project\cppproject\opencv-build -j 20
# 3) 运行某个模块的全部用例（结果打印到 stdout）
D:\project\cppproject\opencv-build\bin\opencv_perf_core.exe --gtest_color=no
```

## 六、注意事项

1. 本次构建关闭了 IPP-ICV 与 FFmpeg（避免联网下载），因此部分函数（如 `cv::resize`、`cvtColor`）比官方发行版慢；视频读写的 ffmpeg 后端也不可用。
2. 缺 `opencv_extra` 数据，DNN / 部分 imgproc、calib3d、stitching、features2d、video 用例只做了跳过处理，数据文件清单见 `opencv_perf_no_data.csv`。补齐数据后设 `OPENCV_TEST_DATA_PATH` 指向数据目录重跑即可。
3. 本机开启了 Smart App Control，会拦截本地编译的未签名 exe；关闭 SAC 后才是原生 Windows 结果。
4. 计时为 perf 框架默认策略（`--perf_min_samples=10`、`--perf_time_limit=3s`），取中位数；CPU 侧由 OpenMP 使用 20 线程。
5. OpenCL 可用（Intel iGPU，走 D3D11 共享表面），所以 core/imgproc/video 里的 `OCL_*` 用例测的是 iGPU + OpenCL 路径，`CPU`/`OCV` 用例是纯 CPU 路径，对比时注意区分。

## 七、附件

- `opencv_perf_results.csv`：全部 PERFSTAT 测量明细（模块/用例/采样数/mean/median/min/stddev）
- `opencv_perf_summary.csv`：各模块用例数统计
- `opencv_perf_results.xlsx`：Summary / PerModuleStats / PerTest / RawMeasurements / Slowest50
- `opencv_perf_no_data.csv`：因缺测试数据被跳过的用例及缺失文件

### 最常缺失的测试数据文件

| 缺失文件 | 影响用例数 |
|---|---|
| `stitching/a1.png` | 188 |
| `cv/shared/pic5.png` | 153 |
| `perf/1920x1080.png` | 101 |
| `cv/detectors_descriptors_evaluation/images_datasets/leuven/img1.png` | 80 |
| `cv/shared/fruits.png` | 72 |
| `cv/optflow/RubberWhale1.png` | 72 |
| `cv/optflow/frames/1080p_01.png` | 72 |
| `cv/optflow/rock_1.bmp` | 71 |
| `stitching/a3.png` | 68 |
| `stitching/s2.jpg` | 68 |
| `cv/optflow/frames/720p_01.png` | 52 |
| `cv/optflow/frames/VGA_01.png` | 36 |
| `cv/optflow/frames/VGA_02.png` | 36 |
| `cv/optflow/frames/720p_02.png` | 36 |
| `cv/video/768x576.avi` | 24 |
