# dlinso v2 - Upstage Solar API test
# PowerShell: cd E:\dlinso_v2 ; .\test_upstage.ps1
# (ASCII only in this file; Korean output comes from Python)
Set-Location $PSScriptRoot
$env:PYTHONIOENCODING = "utf-8"
try {
    [Console]::OutputEncoding = [System.Text.UTF8Encoding]::new()
    $OutputEncoding = [Console]::OutputEncoding
} catch {
    # ignore on older hosts
}

Write-Host ""
Write-Host "========================================"
Write-Host " dlinso v2 - Upstage Solar API Test"
Write-Host "========================================"
Write-Host " Checks UPSTAGE_API_KEY in .env"
Write-Host "========================================"
Write-Host ""

$py = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"
if (-not (Test-Path $py)) { $py = "python" }

& $py scripts\test_upstage_connection.py
$code = $LASTEXITCODE

Write-Host ""
if ($code -eq 0) {
    Write-Host "[OK] Test passed." -ForegroundColor Green
} else {
    Write-Host "[FAIL] Exit code: $code" -ForegroundColor Red
    Write-Host "  - Check UPSTAGE_API_KEY in .env"
    Write-Host "  - Billing: https://console.upstage.ai/billing"
}
Write-Host ""
Read-Host "Press Enter to close"

exit $code
