param(
    [string]$BuildDir = 'D:\project\cppproject\opencv-build',
    [string]$DataPath = 'D:\project\cppproject\opencv_extra\opencv_extra-4.x\testdata',
    [int[]]$Threads  = @(1, 16),
    [string[]]$Modules = @('core','imgproc','imgcodecs','videoio','calib3d','features2d',
                           'objdetect','photo','stitching','video','dnn','gapi')
)

# 用 OpenCV 官方 modules/ts/misc/run.py 驱动 perf 测试（它会自动找 bin\opencv_perf_*.exe 并写 xml 日志）
$py    = 'D:\project\python\Python31011\python.exe'
$runpy = 'D:\project\cppproject\opencv-4.12.0\modules\ts\misc\run.py'
$out   = Join-Path $BuildDir 'bench-results\data-runs'
New-Item -ItemType Directory -Force -Path $out | Out-Null

$env:PATH = (Join-Path $BuildDir 'bin') + ";$env:PATH"
$env:OPENCV_TEST_DATA_PATH = $DataPath          # opencv_extra 测试数据
$env:OPENCV_OPENCL_RUNTIME = 'disabled'         # 只测 CPU，排除 iGPU
$env:OPENCV_FOR_OPENMP_DYNAMIC_DISABLE = '1'    # OpenMP 线程数固定

Push-Location $out
$total = [Diagnostics.Stopwatch]::StartNew()
foreach ($t in $Threads) {
    foreach ($m in $Modules) {
        $log = Join-Path $out "perf_${m}_t$t.log"
        $extra = @()
        if ($m -eq 'gapi') { $extra += '--gtest_filter=-*GPU*' }

        $sw = [Diagnostics.Stopwatch]::StartNew()
        & $py $runpy $BuildDir -t $m --perf_threads=$t --gtest_color=no @extra *> $log
        $code = $LASTEXITCODE
        $sw.Stop()
        Write-Output ("{0,-11} t={1,-2} exit={2} {3,6:N1} min" -f $m, $t, $code, $sw.Elapsed.TotalMinutes)
    }
}
$total.Stop()
Pop-Location
Write-Output ("ALL DONE {0:N1} min -> {1}" -f $total.Elapsed.TotalMinutes, $out)
