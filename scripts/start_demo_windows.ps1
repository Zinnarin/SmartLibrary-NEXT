# Smart Library NEXT V2 - one-command local demo launcher (Windows PowerShell 5.1+)
#   powershell -ExecutionPolicy Bypass -File scripts\start_demo_windows.ps1
# Options:
#   -Reset       delete the local demo database first (fresh NORMAL scenario)
#   -NoBrowser   do not open the browser
#   -Port 8000   change port (server always binds 127.0.0.1 only - never a public interface)
param(
    [switch]$Reset,
    [switch]$NoBrowser,
    [int]$Port = 8000
)

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root
Write-Host "== Smart Library NEXT V2 (local demo) ==" -ForegroundColor Cyan
Write-Host "Project: $Root"

# 1) Python venv (project-local)
$Py = Join-Path $Root ".venv\Scripts\python.exe"
if (-not (Test-Path $Py)) {
    Write-Host "[1/3] Creating Python venv (.venv) ..." -ForegroundColor Yellow
    $base = (Get-Command py -ErrorAction SilentlyContinue)
    if ($base) { py -3.10 -m venv .venv } else { python -m venv .venv }
    & $Py -m pip install --upgrade pip
    & $Py -m pip install -r services\api\requirements.txt
} else {
    Write-Host "[1/3] Python venv OK ($Py)"
}

# 2) Frontend build (served by FastAPI on the same port)
$Dist = Join-Path $Root "apps\web\dist\index.html"
if (-not (Test-Path $Dist)) {
    Write-Host "[2/3] Building frontend (npm ci + npm run build) ..." -ForegroundColor Yellow
    Push-Location (Join-Path $Root "apps\web")
    npm ci --no-audit --no-fund
    npm run build
    Pop-Location
} else {
    Write-Host "[2/3] Frontend build OK (apps\web\dist)"
}

# 3) Run API (+ static frontend). Demo mode enables Scenario Lab; SL_MODE=production disables /api/demo/*.
# BUG-013 fix: refuse to start on a busy port, and never delete a database another server still has open.
$busy = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue
if ($busy) {
    Write-Host "ERROR: port $Port is already in use (pid $($busy[0].OwningProcess)). A demo server is probably already running." -ForegroundColor Red
    Write-Host "       Open http://127.0.0.1:$Port/ , or stop that server (Ctrl+C in its window) first, or use -Port 8010." -ForegroundColor Red
    exit 1
}
$DbFile = if ($env:SL_DB_PATH) { $env:SL_DB_PATH } else { Join-Path $Root "services\api\data\smartlibrary_demo.db" }
if ($Reset) {
    # Windows lets a process delete an SQLite file that another process still has open (verified 14 Oct),
    # so a file lock cannot protect us: refuse -Reset while ANY Smart Library server process is running.
    $running = Get-CimInstance Win32_Process -Filter "Name='python.exe'" -ErrorAction SilentlyContinue |
        Where-Object { $_.CommandLine -like "*app.main:get_app*" }
    if ($running) {
        Write-Host "ERROR: -Reset refused: a Smart Library server is still running (pid $(@($running.ProcessId) -join ', '))." -ForegroundColor Red
        Write-Host "       Stop it first (Ctrl+C in its window). Nothing was deleted." -ForegroundColor Red
        exit 1
    }
    if (Test-Path $DbFile) {
        Remove-Item $DbFile, "$DbFile-wal", "$DbFile-shm" -ErrorAction SilentlyContinue
        if (Test-Path $DbFile) { Write-Host "ERROR: could not delete $DbFile" -ForegroundColor Red; exit 1 }
        Write-Host "Demo database removed: $DbFile (fresh seed on start)."
    }
}
if (-not $env:SL_MODE) { $env:SL_MODE = "demo" }
$Url = "http://127.0.0.1:$Port"
Write-Host "[3/3] Starting server at $Url  (mode=$($env:SL_MODE))" -ForegroundColor Green
Write-Host "      Student:  $Url/"
Write-Host "      Staff:    $Url/#/staff   (demo PIN: staff-demo-2569, override with SL_STAFF_TOKEN)"
Write-Host "      Scenario: $Url/#/lab     CV Lab: $Url/#/cv"
Write-Host "      All data on this screen is SIMULATION unless a source says 'cv'. Ctrl+C to stop."
if (-not $NoBrowser) {
    Start-Job -ScriptBlock { param($u) Start-Sleep -Seconds 3; Start-Process $u } -ArgumentList $Url | Out-Null
}
& $Py -m uvicorn app.main:get_app --factory --app-dir services/api --host 127.0.0.1 --port $Port
