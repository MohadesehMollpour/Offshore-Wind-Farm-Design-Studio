param([int]$Port = 8000)
$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot
if (-not (Test-Path -LiteralPath '.venv\Scripts\python.exe')) { throw 'Missing local virtual environment. Follow README.md setup instructions.' }
if (-not (Test-Path -LiteralPath 'dashboard\dist\index.html')) { throw 'Missing frontend build. Run npm.cmd ci and npm.cmd run build inside dashboard.' }
if ($Port -ne 8000) { throw 'This local release is configured for port 8000. Update the origin allowlist before using a different port.' }
Write-Host 'Offshore Wind Farm Design Studio: http://127.0.0.1:8000'
Write-Host 'Keep this terminal open. Press Ctrl+C to stop.'
& '.\.venv\Scripts\python.exe' -m uvicorn backend.app:app --host 127.0.0.1 --port $Port
