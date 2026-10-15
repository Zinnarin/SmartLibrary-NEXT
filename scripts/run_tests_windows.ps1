# Runs the backend test suite (pytest) and, if the demo server is running on 127.0.0.1:8000,
# the Playwright browser suite (uses the locally installed Microsoft Edge).
#   powershell -ExecutionPolicy Bypass -File scripts\run_tests_windows.ps1
# All generated output goes to artifacts\ (git-ignored) or $env:SL_ARTIFACT_DIR - never to the frozen
# V2 evidence. At the end it verifies that no frozen V2 file was modified (check_ownership.py --frozen-clean).
$ErrorActionPreference = "Continue"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root
$env:PYTHONIOENCODING = "utf-8"
$Art = if ($env:SL_ARTIFACT_DIR) { $env:SL_ARTIFACT_DIR } else { Join-Path $Root "artifacts" }
New-Item -ItemType Directory -Force $Art | Out-Null
Write-Host "Artifacts -> $Art" -ForegroundColor DarkGray

Write-Host "== pytest ==" -ForegroundColor Cyan
& .\.venv\Scripts\python.exe -m pytest -v -rA --junitxml (Join-Path $Art "pytest_junit.xml") 2>&1 | Tee-Object -FilePath (Join-Path $Art "pytest_output.txt")
$pytestExit = $LASTEXITCODE

$e2eExit = $null
try {
    Invoke-RestMethod http://127.0.0.1:8000/api/health -TimeoutSec 3 | Out-Null
    Write-Host "== Playwright e2e (server detected on :8000) ==" -ForegroundColor Cyan
    Push-Location apps\web
    npx playwright test 2>&1 | Tee-Object -FilePath (Join-Path $Art "playwright_output.txt")
    $e2eExit = $LASTEXITCODE
    Pop-Location
} catch {
    Write-Host "Server not running on :8000 -> skipping Playwright (start scripts\start_demo_windows.ps1 first)" -ForegroundColor Yellow
}

Write-Host "== frozen V2 evidence unchanged? ==" -ForegroundColor Cyan
& .\.venv\Scripts\python.exe scripts\check_ownership.py --frozen-clean
$frozenExit = $LASTEXITCODE

Write-Host ("pytest exit={0}  playwright exit={1}  frozen-clean exit={2}" -f $pytestExit, $(if ($null -eq $e2eExit) { "skipped" } else { $e2eExit }), $frozenExit)
if ($pytestExit -ne 0 -or ($e2eExit -ne $null -and $e2eExit -ne 0) -or $frozenExit -ne 0) { exit 1 }
