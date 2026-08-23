# ============================================================
# monitor.ps1 — เปิด serial monitor ดู log จากโดรน
# ============================================================
$root = $PSScriptRoot
$fw = Join-Path $root 'Co-Create_ESP-FLY\Firmware\esp-drone'
$idf = if ($env:IDF_PATH) { $env:IDF_PATH } else { Join-Path $env:USERPROFILE 'esp\esp-idf' }
$exp = Join-Path $idf 'export.ps1'

$port = python -c "import os,serial.tools.list_ports as L; p=os.environ.get('DRONE_PORT'); print(p or next((d.device for d in L.comports() if any(k in (d.description or '').lower() for k in ('cp210','usb-serial','usb jtag','esp32'))), 'COM3'))"

Set-Location $fw
if (Test-Path $exp) { . $exp | Out-Null }
Write-Host "เปิด monitor ที่ $port ... (กด Ctrl+] เพื่อออก)" -ForegroundColor Yellow
idf.py -p $port monitor
