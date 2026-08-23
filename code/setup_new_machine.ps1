# ============================================================
# setup_new_machine.ps1
# ตรวจสอบเครื่องใหม่ก่อนรันโปรเจกต์โดรน (ESP32-S3 + ESP-FLY)
# - หา ESP-IDF (ควรเป็น v5.0)
# - เช็ค Python + ติดตั้ง pyserial
# - หาพอร์ตอนุกรมของบอร์ด
# รันซ้ำได้ ไม่มีผลข้างเคียง
# ============================================================
$ErrorActionPreference = 'Stop'
$ProjectRoot = $PSScriptRoot

Write-Host "======================================================" -ForegroundColor Cyan
Write-Host "  ตรวจสอบเครื่องสำหรับโปรเจกต์โดรน (ESP32-S3)" -ForegroundColor Cyan
Write-Host "======================================================" -ForegroundColor Cyan

# ---------- 1) ESP-IDF ----------
Write-Host "`n[1/4] ตรวจหา ESP-IDF ..." -ForegroundColor Yellow
$idfFound = $false
$candidates = @()
if ($env:IDF_PATH) { $candidates += $env:IDF_PATH }
$candidates += "$env:USERPROFILE\esp\esp-idf"
$candidates += "C:\Espressif\frameworks\esp-idf-v5.0"
foreach ($c in $candidates) {
    if ($c -and (Test-Path (Join-Path $c 'export.ps1'))) {
        Write-Host "  พบ ESP-IDF ที่: $c" -ForegroundColor Green
        $idfFound = $true
        # ลองเช็คเวอร์ชัน
        $vFile = Join-Path $c 'version.txt'
        if (Test-Path $vFile) {
            $ver = (Get-Content $vFile -TotalCount 1).Trim()
            Write-Host "  เวอร์ชัน: $ver" -ForegroundColor Green
            if ($ver -notmatch '^v5\.0') {
                Write-Host "  [!] เวอร์ชันไม่ใช่ v5.0 — เฟิร์มแวร์นี้ออกแบบสำหรับ v5.0" -ForegroundColor Red
            }
        }
        break
    }
}
if (-not $idfFound) {
    Write-Host "  [!] ยังไม่พบ ESP-IDF" -ForegroundColor Red
    Write-Host "      ติดตั้ง v5.0 จาก: https://dl.espressif.com/dl/esp-idf/" -ForegroundColor Red
    Write-Host "      หรือ Espressif IDE แล้วเลือกเวอร์ชัน v5.0" -ForegroundColor Red
}

# ---------- 2) Python ----------
Write-Host "`n[2/4] ตรวจ Python ..." -ForegroundColor Yellow
try {
    $pyVer = python --version 2>&1
    Write-Host "  $pyVer" -ForegroundColor Green
} catch {
    Write-Host "  [!] ไม่พบ Python — ติดตั้งจาก https://www.python.org (ติ๊ก Add to PATH)" -ForegroundColor Red
}

# ---------- 3) pyserial ----------
Write-Host "`n[3/4] ตรวจ pyserial ..." -ForegroundColor Yellow
try {
    python -c "import serial; print('  pyserial', serial.__version__)" 2>$null
    if ($LASTEXITCODE -ne 0) { throw }
} catch {
    Write-Host "  กำลังติดตั้ง pyserial ..." -ForegroundColor Yellow
    python -m pip install pyserial
}

# ---------- 4) พอร์ตอนุกรม ----------
Write-Host "`n[4/4] หาพอร์ตอนุกรมของบอร์ด ..." -ForegroundColor Yellow
$ports = @()
try {
    $ports = python -c @"
import serial.tools.list_ports
for p in serial.tools.list_ports.comports():
    d = (p.description or '') + ' ' + (p.device or '')
    if any(k in d.lower() for k in ('cp210','usb-serial','usb serial','usb jtag','esp32')):
        print(p.device, '|', p.description)
"@
} catch {}
if ($ports) {
    foreach ($pt in $ports) { Write-Host "  $pt" -ForegroundColor Green }
} else {
    Write-Host "  (ไม่พบพอร์ตอัตโนมัติ — เช็ค Device Manager หรือตั้งตัวแปร DRONE_PORT='COMx')" -ForegroundColor Gray
}

# ---------- สรุปคำสั่ง ----------
Write-Host "`n======================================================" -ForegroundColor Cyan
Write-Host "  ขั้นตอนถัดไป" -ForegroundColor Cyan
Write-Host "======================================================" -ForegroundColor Cyan
Write-Host @"

1) Build + Flash เฟิร์มแวร์โดรน:
   cd '$ProjectRoot\Co-Create_ESP-FLY\Firmware\esp-drone'
   & 'C:\Users\คุณ\esp\esp-idf\export.ps1' | Out-Null
   idf.py fullclean
   idf.py build
   idf.py -p COMx flash        # เปลี่ยน COMx เป็นพอร์ตจริง

2) ต่อ WiFi โดรน:  ESP-DRONE_9C139EF3414D  /  รหัส 12345678

3) ทดสอบ Python:
   cd '$ProjectRoot'
   python diag_nan.py

4) เปิดสื่อการสอน:
   start '$ProjectRoot\teaching_materials\index.html'

ดูรายละเอียดเพิ่มใน MIGRATION.md
"@
Write-Host "======================================================" -ForegroundColor Cyan
