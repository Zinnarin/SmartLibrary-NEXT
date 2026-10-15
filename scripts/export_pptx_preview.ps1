# Opens a deck in the locally installed PowerPoint (COM), exports a PDF and one PNG per slide into
# presentation\preview\ to verify it opens and Thai text renders. Also lists the fonts the deck uses.
#   powershell -ExecutionPolicy Bypass -File scripts\export_pptx_preview.ps1 [-Deck presentation\progress_update_v2.pptx]
# Safety: if PowerPoint is already running (e.g. you are editing a deck), it is NOT quit - only the copy opened here is closed.
param([string]$Deck = "presentation\progress_update.pptx")
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
$Pptx = Join-Path $Root $Deck
$Out = Join-Path $Root "presentation\preview"
New-Item -ItemType Directory -Force $Out | Out-Null
$wasRunning = [bool](Get-Process POWERPNT -ErrorAction SilentlyContinue)
$app = New-Object -ComObject PowerPoint.Application
try {
    $pres = $app.Presentations.Open($Pptx, $true, $false, $false)  # ReadOnly, no window
    "Opened: $Deck slides=$($pres.Slides.Count) width=$($pres.PageSetup.SlideWidth) height=$($pres.PageSetup.SlideHeight)"
    $fonts = @(); foreach ($f in $pres.Fonts) { $fonts += "$($f.Name) (embedded=$($f.Embedded))" }
    "Fonts used: " + ($fonts -join "; ")
    $pres.SaveAs((Join-Path $Out "progress_update.pdf"), 32)  # ppSaveAsPDF
    foreach ($s in $pres.Slides) {
        $f = Join-Path $Out ("slide_{0:D2}.png" -f $s.SlideIndex)
        $s.Export($f, "PNG", 1600, 900)
        "exported $f"
    }
    $pres.Close()
} finally {
    if (-not $wasRunning) { $app.Quit() } else { "PowerPoint was already running: left open (not quit)." }
    [System.Runtime.Interopservices.Marshal]::ReleaseComObject($app) | Out-Null
}
