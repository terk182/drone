# ESP-FLY Drone — Flashing via ESP-Launchpad

โดรนเพื่อการศึกษา ESP-FLY (ESP32-S3 SuperMini + MPU-6050 clone)

## สิ่งที่ต้องเตรียม

1. เบราว์เซอร์ **Chrome หรือ Edge** (WebSerial API — ต้องเป็น HTTPS)
2. สาย USB ที่ **ส่งข้อมูลได้** (ไม่ใช่สายชาร์จอย่างเดียว)
3. บอร์ดโดรน ESP32-S3 SuperMini

## วิธี flash (3 ขั้นตอน)

### 1. เปิดหน้า flash
เปิด URL ที่ครูให้มา (หน้า ESP-Launchpad)

### 2. เชื่อมต่อ
- เสียบสาย USB เข้าบอร์ด (ขั้ว USB-C)
- คลิกปุ่ม **Connect** (มุมบน)
- เลือกพอร์ต **USB Serial Device (COMxx)** แล้วกด Connect

### 3. กด Flash
- รอจนหน้าจอขึ้น `Chip is ESP32-S3` / `Connected`
- คลิกปุ่ม **Flash** ตรงกลาง
- รอจนจบ (ขึ้น `Flash done` / บาร์เต็ม)

> ⚠️ **สำคัญมาก:** หลัง flash เสร็จ ให้ **ถอดสาย USB แล้วเสียบใหม่ 1 ครั้ง**
> (IMU clone จะล็อกหลุดถ้าไม่รีเซ็ตไฟจริง — บอร์ดอาจ reboot วนถ้าไม่ทำ)

## ตรวจสอบว่าเรียบร้อย

เสียบกลับแล้ว เปิด WiFi แล้วหา SSID: `ESP-DRONE_XXXXXXXXXXXX` (รหัส `12345678`)
ถ้าเจอ = flash สำเร็จ

## แก้ปัญหาที่พบบ่อย

| ปัญหา | วิธีแก้ |
|---|---|
| กด Connect แล้วไม่เห็นพอร์ต | ใช้ Chrome/Edge, ต่อสายข้อมูล, ลองพอร์ต USB อื่น |
| Flash ค้าง/Write timeout | เปลี่ยนสาย, เสียบพอร์ตหลังเครื่อง, ลองกดขั้ว USB ค้างไว้ |
| เสียบใหม่แล้วไม่มี WiFi | ถอด-เสียบ USB อีกครั้ง (power cycle จริง) |
| บอร์ด reboot วน | ถอด-เสียบ USB จริงเพื่อปลดล็อก IMU |
