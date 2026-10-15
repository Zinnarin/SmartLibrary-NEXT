# Runs the backend test suite (pytest) and, if the demo server is running on 127.0.0.1:8000,
# the Playwright browser smoke path (uses the locally installed Microsoft Edge).
#   powershell -ExecutionPolicy Bypass -File scripts\run_tests_windows.ps1
$ErrorActionPreference = "Continue"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root
$env:PYTHONIOENCODING = "utf-8"
Write-Host "== pytest ==" -ForegroundColor Cyan
& .\.venv\Scripts\python.exe -m pytest -v -rA 2>&1 | Tee-Object -FilePath evidence\pytest_output.txt
try {
    Invoke-RestMethod http://127.0.0.1:8000/api/health -TimeoutSec 3 | Out-Null
    Write-Host "== Playwright e2e (server detected on :8000) ==" -ForegroundColor Cyan
    Push-Location apps\web
    npx playwright test 2>&1 | Tee-Object -FilePath ..\..\evidence\playwright_output.txt
    Pop-Location
} catch {
    Write-Host "Server not running on :8000 -> skipping Playwright (start scripts\start_demo_windows.ps1 first)" -ForegroundColor Yellow
}
