# ============================================================
# flash_board.ps1 — Flash เฟิร์มแวร์ลง 1 บอร์ด (สำหรับเตรียมหลายบอร์ด)
# - หาพอร์ตอัตโนมัติ (หรือตั้ง $env:DRONE_PORT='COMx')
# - ใช้ baud 115200 (เสถียรกับสาย USB ที่ไม่ค่อยนิ่ง)
# รันทีละบอร์ด: เสียบ USB -> รันสคริปต์ -> ถอด-เสียบ USB ใหม่ (ปลดล็อก IMU)
# ============================================================
$ErrorActionPreference = 'Continue'
$root = $PSScriptRoot
$fw = Join-Path $root 'Co-Create_ESP-FLY\Firmware\esp-drone'
$bin = Join-Path $fw 'build\ESPDrone.bin'

if (-not (Test-Path $bin)) {
    Write-Host "[X] ไม่พบ $bin - build ก่อน: cd '$fw'; idf.py build" -ForegroundColor Red
    exit 1
}

# --- หาพอร์ต ---
$port = $env:DRONE_PORT
if (-not $port) {
    $ports = python -c "import serial.tools.list_ports as L; print(' '.join(p.device for p in L.comports()))" 2>$null
    $port = ($ports -split ' ' | Where-Object { $_ -match 'COM' } | Select-Object -First 1)
}
if (-not $port) {
    Write-Host "[X] ไม่พบพอร์ตอนุกรม - เสียบ USB บอร์ดก่อน หรือตั้ง `$env:DRONE_PORT='COMx'" -ForegroundColor Red
    exit 1
}
Write-Host "[*] พอร์ต: $port" -ForegroundColor Yellow

# --- flash ---
cd $fw
$exp = if ($env:IDF_PATH) { Join-Path $env:IDF_PATH 'export.ps1' } else { Join-Path $env:USERPROFILE 'esp\esp-idf\export.ps1' }
if (Test-Path $exp) { . $exp | Out-Null }

python "$env:IDF_PATH\components\esptool_py\esptool\esptool.py" --chip esp32s3 -b 115200 -p $port --before default_reset --after hard_reset write_flash --flash_mode dio --flash_size detect --flash_freq 80m 0x0 build\bootloader\bootloader.bin 0x8000 build\partition_table\partition-table.bin 0x10000 build\ESPDrone.bin
if ($LASTEXITCODE -ne 0) {
    Write-Host "[X] FLASH FAILED" -ForegroundColor Red
    exit $LASTEXITCODE
}
Write-Host "`n[OK] Flash สำเร็จ!" -ForegroundColor Green
Write-Host "     ต่อไป: ถอด-เสียบ USB ใหม่ (ปลดล็อก IMU) แล้วต่อบอร์ดถัดไป" -ForegroundColor Cyan
