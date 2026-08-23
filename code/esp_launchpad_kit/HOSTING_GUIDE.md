# คู่มือเผยแพร่เฟิร์มแวร์โดรนผ่าน ESP-Launchpad (ฉบับครู)

เป้าหมาย: ให้นักเรียนเปิด URL เดียว แล้วกดปุ่ม Flash ผ่านเบราว์เซอร์ (ไม่ต้องติดตั้งอะไร)

## ไฟล์ในชุดนี้

```
esp_launchpad_kit/
├── bin/
│   └── merged.bin              (ไฟล์เดียวจบ! รวม bootloader+partition+app, flash ที่ 0x0)
├── config.toml                 (ตัวตั้งค่าของ ESP-Launchpad — ต้องแก้ BASE_URL)
├── README.md                   (คำแนะนำนักเรียน แสดงในหน้า flash)
└── HOSTING_GUIDE.md            (ไฟล์นี้)

หมายเหตุ: bin/ ยังมี bootloader.bin, partition-table.bin, ESPDrone.bin แยกไว้
(สำรอง/ใช้กับวิธี DIY หรือ esptool ทั่วไป)
```

## ทางเลือก A: GitHub Pages (แนะนำ — ฟรี, CORS ผ่าน)

1. สร้าง repo ใหม่บน GitHub (ชื่ออะไรก็ได้ เช่น `esp-drone-fw`) — ตั้งเป็น **Public**
2. อัปโหลดไฟล์: `bin/merged.bin`, `config.toml`, `README.md`
3. เปิด Settings → Pages → Source: **Deploy from a branch** → เลือก `main` + root → Save
4. รอ ~1 นาที แล้วได้ URL: `https://<ชื่อผู้ใช้>.github.io/esp-drone-fw/`
5. **แก้ `config.toml`**: แทนที่ `__BASE_URL__` ทุกจุดด้วย `https://<ชื่อผู้ใช้>.github.io/esp-drone-fw`
6. อัปโหลด `config.toml` ที่แก้แล้วทับ

**URL ให้นักเรียน:**
```
https://espressif.github.io/esp-launchpad/minimal-launchpad/?flashConfigURL=https://<ชื่อผู้ใช้>.github.io/esp-drone-fw/config.toml
```

## ทางเลือก B: Netlify Drop (เร็วสุด — ลากวาง)

1. ไป https://app.netlify.com/drop (ล็อกอิน Google/GitHub)
2. ลากโฟลเดอร์ `esp_launchpad_kit` ลงไป → ได้ URL เช่น `https://xxx.netlify.app`
3. แก้ `config.toml` แทนที่ `__BASE_URL__` ด้วย URL นั้น แล้วอัปโหลดทับ (Netlify Drop ใหม่ หรือ Deploy)
4. ใช้ URL เดียวกับรูปแบบด้านบน (ชี้ไป config.toml ของ Netlify)

> Netlify/Vercel/Cloudflare Pages ส่ง CORS header อัตโนมัติ — ใช้ได้กับ ESP-Launchpad

## หมายเหตุสำคัญ

- **ทุกไฟล์ (bin + config.toml + README.md) ต้อง CORS-enabled** — GitHub Pages/Netlify ผ่านอยู่แล้ว
- ถ้า host ไม่ CORS ให้เติม `&crossDomain=true` ต่อท้าย URL (proxy ของ Espressif — ใช้กับ TOML ได้ แต่ **bin ยังต้อง CORS เอง**)
- minimal-launchpad ใช้ baudrate flash 460800 — ถ้าบอร์ดไหน flash ไม่ผ่าน (USB ไม่เสถียร) ให้ใช้หน้า DIY ของ launchpad หลัก:
  `https://espressif.github.io/esp-launchpad/` → แท็บ DIY → ตั้ง Baud rate = **115200** ใน Settings → เลือก `merged.bin` + address `0x0` → Flash
- วิธีสร้าง `merged.bin` ใหม่ (เมื่อ build เฟิร์มแวร์อัปเดต):
  ```
  python .../esptool.py --chip esp32s3 merge_bin -o merged.bin --flash_mode dio --flash_size 4MB --flash_freq 80m \
      0x0 build/bootloader/bootloader.bin 0x8000 build/partition_table/partition-table.bin 0x10000 build/ESPDrone.bin
  ```
  (คำสั่งเต็มอยู่ใน build: ใช้ `idf.py` env เดียวกับ flash_board.ps1)
- หลัง flash เสร็จทุกครั้ง: **ถอด-เสียบ USB ใหม่** (ปลดล็อก IMU) — เหมือนขั้นตอนที่ทำกับทุกบอร์ด
