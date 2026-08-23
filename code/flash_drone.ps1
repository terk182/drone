# ============================================================
# flash_drone.ps1 — กดปุ่มเดียว: Build + Flash เฟิร์มแวร์โดรน
# หา ESP-IDF และพอร์ตอนุกรมให้อัตโนมัติ
# ============================================================
$ErrorActionPreference = 'Continue'
$root = $PSScriptRoot
$fw = Join-Path $root 'Co-Create_ESP-FLY\Firmware\esp-drone'

if (-not (Test-Path $fw)) {
    Write-Host "ไม่พบโฟลเดอร์เฟิร์มแวร์: $fw" -ForegroundColor Red
    exit 1
}

# --- หา ESP-IDF ---
$idf = $env:IDF_PATH
if (-not $idf) { $idf = Join-Path $env:USERPROFILE 'esp\esp-idf' }
$exp = Join-Path $idf 'export.ps1'
if (-not (Test-Path $exp)) {
    Write-Host "ไม่พบ ESP-IDF ที่ $idf — ต้องติดตั้ง v5.0 ก่อน" -ForegroundColor Red
    exit 1
}

# --- หาพอร์ตอนุกรม ---
$port = python -c "import os,serial.tools.list_ports as L; p=os.environ.get('DRONE_PORT'); print(p or next((d.device for d in L.comports() if any(k in (d.description or '').lower() for k in ('cp210','usb-serial','usb jtag','esp32'))), 'COM3'))"

Set-Location $fw
. $exp | Out-Null

Write-Host "`n[1/2] Build ..." -ForegroundColor Yellow
idf.py build
if ($LASTEXITCODE -ne 0) {
    Write-Host "BUILD FAILED" -ForegroundColor Red
    exit $LASTEXITCODE
}

Write-Host "`n[2/2] Flash ไปที่ $port ..." -ForegroundColor Yellow
idf.py -p $port flash
if ($LASTEXITCODE -ne 0) {
    Write-Host "FLASH FAILED" -ForegroundColor Red
    exit $LASTEXITCODE
}

Write-Host "`nสำเร็จ! เปิดเมนู -> Monitor เพื่อดู log หรือกดปุ่ม RESET บนบอร์ด" -ForegroundColor Green
