# 🚚 คู่มือย้ายโปรเจกต์โดรนไปรันบนเครื่องอื่น

คู่มือนี้สำหรับย้าย **ชุดโค้ดโดรนทั้งหมด** (เฟิร์มแวร์ + สคริปต์ทดสอบ + สื่อการสอน) ไปรันบนคอมพิวเตอร์เครื่องอื่น เช่น คอมพิวเตอร์ห้องเรียน / เครื่องนักเรียน

---

## 🎓 สำหรับห้องเรียน (ใช้เครื่องนี้โดยตรง)

เครื่องนี้พร้อมใช้สอนแล้ว — มี **เมนูกดปุ่มเดียว**:

| วิธีเปิด | สิ่งที่ได้ |
|---|---|
| ดับเบิลคลิก **`Drone-Menu`** บน Desktop | เมนูห้องเรียน (ภาษาไทย) |
| หรือดับเบิลคลิก `start_teaching.bat` ในโฟลเดอร์ | เหมือนกัน |

เมนูมีให้เลือก:
1. **เปิดสื่อการสอน** — เปิด `teaching_materials\index.html`
2. **Build + Flash เฟิร์มแวร์โดรน** — กดปุ่มเดียว (หา ESP-IDF + พอร์ตให้อัตโนมัติ)
3. **เปิด Monitor** — ดู log จากโดรน
4. **ตรวจระบบก่อนใช้ (Pre-flight)** — เช็ค WiFi/IMU/attitude อัตโนมัติ (รัน `python preflight.py`)
5. **เปิดคู่มือย้ายเครื่อง**

ไฟล์สำรองเฟิร์มแวร์ที่ใช้งานได้: `backup_firmware\ESPDrone_good.bin`
(ถ้านักเรียนทำเฟิร์มแวร์พัง ให้ flash คืนจากไฟล์นี้: `idf.py -p COMx flash` โดยแทนที่ `build\ESPDrone.bin` หรือ build ใหม่จากซอร์สที่แก้อัตโนมัติ)

---

## 📦 สิ่งที่ต้องย้าย (Copy ทั้งโฟลเดอร์นี้)

ให้คัดลอกทั้งโฟลเดอร์ `drone_1` (หรือเลือกเฉพาะโฟลเดอร์ย่อย) ไปเครื่องใหม่ เช่น ไปที่ `D:\drone_1` เหมือนเดิม:

| โฟลเดอร์/ไฟล์ | หน้าที่ | จำเป็นไหม |
|---|---|---|
| `Co-Create_ESP-FLY\Firmware\esp-drone\` | เฟิร์มแวร์โดรน (แก้ + flash) | ✅ จำเป็น |
| `imu_test\` | โปรเจกต์ทดสอบ IMU แบบ standalone | ✅ แนะนำ |
| `cflib-esplane\` | ไลบรารี cflib (UDP driver + patch แล้ว) | ✅ จำเป็นสำหรับ Python |
| `*.py` (drone_test, diag_nan, read_boot, ...) | สคริปต์ทดสอบ/ตรวจ | ✅ แนะนำ |
| `teaching_materials\index.html` | สื่อการสอน | ✅ แนะนำ |

> ⚠️ **ห้ามคัดลอกโฟลเดอร์ `build/`** (ใน esp-drone และ imu_test) — มันเก็บ path เฉพาะเครื่องเดิม ต้องลบทิ้งแล้ว build ใหม่บนเครื่องใหม่

---

## 🖥️ สิ่งที่ต้องติดตั้งบนเครื่องใหม่ (ครั้งแรกเท่านั้น)

### 1. ติดตั้ง ESP-IDF v5.0 (สำคัญ: ต้องเป็น v5.0 ตามที่เฟิร์มแวร์ใช้)
- ดาวน์โหลดตัวติดตั้ง: https://dl.espressif.com/dl/esp-idf/ (เลือก **v5.0**)
- หรือใช้ Espressif IDE แล้วเลือกเวอร์ชัน v5.0
- หลังติดตั้งจะมีโฟลเดอร์ `C:\Users\<ชื่อผู้ใช้>\esp\esp-idf`

> ⚠️ ถ้าติดตั้งเวอร์ชันอื่น (v5.1+, v6.x) โค้ด I2C ในเฟิร์มแวร์อาจ compile ไม่ผ่าน (API เปลี่ยน) — **ควรใช้ v5.0 เท่านั้น**

### 2. ติดตั้ง Python 3.x
- ดาวน์โหลดจาก https://www.python.org/downloads/ (ติ๊ก **Add to PATH** ตอนติดตั้ง)
- เปิด PowerShell แล้วติดตั้งไลบรารี:
  ```powershell
  python -m pip install pyserial
  ```

### 3. (ไม่บังคับ) ติดตั้ง Git
- ใช้เผื่อ clone เฟิร์มแวร์ต้นทางใหม่ แต่ไม่จำเป็น เพราะเราคัดลอกโฟลเดอร์มาแล้ว

---

## 🚀 ขั้นตอนรันบนเครื่องใหม่

### ขั้น A: ตรวจว่าพร้อม
```powershell
# เปิด PowerShell แล้วรันสคริปต์ตั้งค่าอัตโนมัติ (อยู่กับโฟลเดอร์โปรเจกต์)
cd D:\drone_1
.\setup_new_machine.ps1
```
สคริปต์จะตรวจ ESP-IDF, Python, pyserial และแนะนำขั้นตอนถัดไปให้เอง

### ขั้น B: Build + Flash เฟิร์มแวร์โดรน
```powershell
cd D:\drone_1\Co-Create_ESP-FLY\Firmware\esp-drone
& 'C:\Users\<ชื่อผู้ใช้>\esp\esp-idf\export.ps1' | Out-Null   # เปิด environment
idf.py fullclean        # ล้าง build เก่า (ครั้งแรกหลังย้าย)
idf.py build            # compile
idf.py -p COMx flash    # ลงบอร์ด (COMx = พอร์ตอนุกรมของบอร์ดบนเครื่องนี้)
```
- พอร์ตอนุกรมบนเครื่องใหม่อาจไม่ใช่ COM3 — ดูได้จาก Device Manager > Ports (COM & LPT)
- เมื่อ boot สำเร็จควรเห็น `MPU6050 WHO_AM_I=0x38` → `I2C connection [OK]` → `Ready to fly.`

### ขั้น C: ทดสอบ IMU (ไม่บังคับ)
```powershell
cd D:\drone_1\imu_test
& 'C:\Users\<ชื่อผู้ใช้>\esp\esp-idf\export.ps1' | Out-Null
idf.py fullclean
idf.py build
idf.py -p COMx flash   # ระวัง: จะทับเฟิร์มแวร์โดรน — ทดสอบเสร็จต้อง flash โดรนกลับ
```
> หลังทดสอบ IMU เสร็จ ต้องกลับไป flash เฟิร์มแวร์โดรนใหม่ (ขั้น B) เสมอ

### ขั้น D: เชื่อมต่อ WiFi + ทดสอบด้วย Python
1. เชื่อมต่อ WiFi คอมพิวเตอร์เข้ากับ AP ของโดรน: `ESP-DRONE_9C139EF3414D` รหัส `12345678`
2. รันสคริปต์ทดสอบ (path ในสคริปต์ปรับเป็นอัตโนมัติแล้ว ไม่ต้องแก้):
   ```powershell
   cd D:\drone_1
   python diag_nan.py              # ตรวจ acc/gyro/attitude
   python drone_logstream_test.py  # stream ค่า log จากโดรน
   ```

### ขั้น E: เปิดสื่อการสอน
```powershell
start D:\drone_1\teaching_materials\index.html
```

---

## ⚠️ ข้อควรระวัง / ปัญหาที่พบบ่อยเมื่อย้ายเครื่อง

| ปัญหา | วิธีแก้ |
|---|---|
| `idf.py` ไม่รู้จักคำสั่ง | ยังไม่ได้รัน `export.ps1` ก่อน หรือ ESP-IDF ไม่ได้ติดตั้งเป็น v5.0 |
| build error เกี่ยวกับ `i2c_master_cmd_begin` / driver | ESP-IDF เวอร์ชันไม่ตรง — ต้องเป็น **v5.0** |
| flash ไม่เจอพอร์ต | เช็คชื่อพอร์ตใหม่ใน Device Manager / ใช้ `python read_boot.py` เพื่อให้สคริปต์หาพอร์ตอัตโนมัติ หรือตั้ง `$env:DRONE_PORT='COMx'` |
| Python import cflib ไม่เจอ | ต้องรันจากโฟลเดอร์ที่มีโฟลเดอร์ `cflib-esplane` อยู่ข้าง ๆ (สคริปต์หา path เองแล้ว) หรือรัน `python -m pip install pyserial` |
| เชื่อมต่อ cflib ค้างที่ "Requesting memories" | ใช้ fork `cflib-esplane` ที่คัดลอกมานี้ (patch memory service ไว้แล้ว) |
| boot แล้ว IMU หาย (WHO_AM_I=0x00 วนรีสตาร์ท) | ถอด-เสียบ USB ใหม่ (power cycle) — เป็นปัญหา hardware สาย/คอนแทคโมดูล IMU |
| โดรนตอบสนอง แต่ Windows เด้งกลับ WiFi บ้าน | ลบโปรไฟล์ WiFi บ้าน หรือต่ออินเทอร์เน็ตผ่านสายแลนแทน |

---

## 🔧 อธิบายสคริปต์ `setup_new_machine.ps1`
สคริปต์ตรวจสอบบนเครื่องใหม่โดยอัตโนมัติ:
1. หา ESP-IDF (จาก `IDF_PATH` หรือ path มาตรฐาน) และเช็คเวอร์ชัน
2. เช็ค Python และติดตั้ง `pyserial`
3. หาพอร์ตอนุกรมของบอร์ด (CP210x/USB Serial)
4. แสดงคำสั่ง build/flash ที่ควรใช้

รันได้เรื่อย ๆ ไม่มีผลข้างเคียง (read-only + pip install pyserial เท่านั้น)
