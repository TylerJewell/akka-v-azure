<#
  PostToolUse hook: regenerate a battlecard's PDF when its .html is edited.
  Wired into .claude/settings.json (matcher Edit|Write|MultiEdit). Reads the hook
  event JSON on stdin, and if the edited file is battlecards/battlecard-*.html,
  regenerates the matching .pdf. Always exits 0 so it never blocks a tool call.
#>
$raw = [Console]::In.ReadToEnd()
try { $j = $raw | ConvertFrom-Json } catch { exit 0 }
$fp = $j.tool_input.file_path
if (-not $fp) { exit 0 }
if ($fp -match 'battlecard-[^\\/]*\.html$') {
  try { & "$PSScriptRoot\build-pdfs.ps1" -File $fp | Out-Null } catch { }
}
exit 0
