<#
  Regenerate battlecard PDFs from their .html source via headless Edge.

  Usage:
    build-pdfs.ps1                 # regenerate every battlecard-*.pdf
    build-pdfs.ps1 -File foo.html  # regenerate only foo.pdf

  The .pdf renders the .html (the styled print version). Kept in sync by the
  PostToolUse hook in .claude/settings.json, which calls this on battlecard edits.
#>
param([string]$File)

$edge = @(
  "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
  "C:\Program Files\Microsoft\Edge\Application\msedge.exe"
) | Where-Object { Test-Path $_ } | Select-Object -First 1
if (-not $edge) { Write-Error "msedge.exe not found"; exit 1 }

if ($File) {
  if (-not (Test-Path $File)) { Write-Error "not found: $File"; exit 1 }
  $htmls = @(Get-Item $File)
} else {
  $htmls = Get-ChildItem -Path $PSScriptRoot -Filter 'battlecard-*.html'
}

foreach ($h in $htmls) {
  if ($h.Extension -ne '.html') { continue }
  $pdf     = [System.IO.Path]::ChangeExtension($h.FullName, '.pdf')
  $uri     = 'file:///' + ($h.FullName -replace '\\','/')
  $profile = Join-Path $env:TEMP ("edge-pdf-" + [System.Guid]::NewGuid().ToString('N'))
  $log     = Join-Path $env:TEMP ("edge-pdf-" + [System.Guid]::NewGuid().ToString('N') + ".log")
  $args = @(
    '--headless=new','--disable-gpu','--no-first-run','--disable-logging','--log-level=3',
    "--user-data-dir=$profile",'--no-pdf-header-footer',"--print-to-pdf=$pdf",$uri
  )
  # Start-Process avoids the PS 5.1 NativeCommandError wrapping of Edge's stderr.
  Start-Process -FilePath $edge -ArgumentList $args -Wait -NoNewWindow `
    -RedirectStandardError $log -RedirectStandardOutput "$log.out"
  for ($i = 0; $i -lt 25 -and -not (Test-Path $pdf); $i++) { Start-Sleep -Milliseconds 200 }
  Remove-Item -Recurse -Force $profile, $log, "$log.out" -ErrorAction SilentlyContinue
  if (Test-Path $pdf) { Write-Output ("regenerated {0}" -f (Split-Path $pdf -Leaf)) }
  else { Write-Output ("FAILED {0}" -f (Split-Path $pdf -Leaf)) }
}
