# Render the first slide of a PPTX to PNG using the PowerPoint COM object.
# Usage: powershell -File render_pptx.ps1 -Pptx <path> -OutPng <path> [-Width 1672] [-Height 941]
param(
    [Parameter(Mandatory=$true)] [string]$Pptx,
    [Parameter(Mandatory=$true)] [string]$OutPng,
    [int]$Width = 1672,
    [int]$Height = 941
)

$ErrorActionPreference = 'Stop'
$ppt = $null
$pres = $null
try {
    $ppt = New-Object -ComObject PowerPoint.Application
    # VisibleState could be set; keep it minimal. Open ReadOnly, no untitled, no window.
    $pres = $ppt.Presentations.Open($Pptx, $true, $false, $false)
    $slide = $pres.Slides.Item(1)
    $slide.Export($OutPng, 'PNG', $Width, $Height)
    Write-Output "rendered: $OutPng"
}
finally {
    if ($pres) { try { $pres.Close() } catch {} }
    if ($ppt)  { try { $ppt.Quit() } catch {} }
    [System.Runtime.InteropServices.Marshal]::ReleaseComObject($ppt) | Out-Null
    [GC]::Collect()
    [GC]::WaitForPendingFinalizers()
}
