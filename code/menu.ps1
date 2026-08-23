# ============================================================
# menu.ps1 — เมนูหลักสำหรับห้องเรียน (เรียกผ่าน start_teaching.bat)
# ============================================================
$root = $PSScriptRoot

function Show-Menu {
    Clear-Host
    Write-Host "=============================================" -ForegroundColor Cyan
    Write-Host "   🚁 โดรน ESP32-S3 — เมนูห้องเรียน" -ForegroundColor Cyan
    Write-Host "=============================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "  1) 📖 เปิดสื่อการสอน"
    Write-Host "  2) 🔧 Build + Flash เฟิร์มแวร์โดรน"
    Write-Host "  3) 📟 เปิด Monitor (ดู log จากโดรน)"
    Write-Host "  4) ✅ ตรวจระบบก่อนใช้ (Pre-flight)"
    Write-Host "  5) 📋 เปิดคู่มือย้ายเครื่อง (MIGRATION)"
    Write-Host "  0) 🚪 ออกจากเมนู"
    Write-Host ""
}

do {
    Show-Menu
    $choice = Read-Host "เลือกเมนู"
    switch ($choice) {
        '1' {
            Write-Host "เปิดสื่อการสอน ..." -ForegroundColor Yellow
            Start-Process (Join-Path $root 'teaching_materials\index.html')
            Read-Host "กด Enter เพื่อกลับเมนู"
        }
        '2' {
            & (Join-Path $root 'flash_drone.ps1')
            Read-Host "กด Enter เพื่อกลับเมนู"
        }
        '3' {
            & (Join-Path $root 'monitor.ps1')
            Read-Host "กด Enter เพื่อกลับเมนู"
        }
        '4' {
            Write-Host "ตรวจระบบ ..." -ForegroundColor Yellow
            python (Join-Path $root 'preflight.py')
            Read-Host "กด Enter เพื่อกลับเมนู"
        }
        '5' {
            Write-Host "เปิดคู่มือ ..." -ForegroundColor Yellow
            Start-Process (Join-Path $root 'MIGRATION.md')
            Read-Host "กด Enter เพื่อกลับเมนู"
        }
        '0' { Write-Host "บาย!" -ForegroundColor Cyan }
        default { Write-Host "ไม่รู้จักตัวเลือก" -ForegroundColor Red; Read-Host "กด Enter" }
    }
} while ($choice -ne '0')
