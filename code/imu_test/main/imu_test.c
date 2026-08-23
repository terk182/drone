/*
 * Standalone MPU-6050 / MPU-6500 register test for ESP32-S3.
 * Reads WHO_AM_I, PWR_MGMT registers, and raw accel/gyro/temp directly
 * over I2C on SDA=GPIO8, SCL=GPIO9 to verify the sensor.
 */
#include <stdio.h>
#include <string.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "driver/i2c.h"
#include "esp_log.h"

#define I2C_PORT  I2C_NUM_0
#define SDA_PIN   8
#define SCL_PIN   9
#define MPU_ADDR  0x68

#define REG_WHO_AM_I     0x75
#define REG_PWR_MGMT_1   0x6B
#define REG_PWR_MGMT_2   0x6C
#define REG_ACCEL_CONFIG 0x1C
#define REG_GYRO_CONFIG  0x1B
#define REG_ACCEL_XOUT_H 0x3B
#define REG_TEMP_OUT_H   0x41
#define REG_GYRO_XOUT_H  0x43

static const char *TAG = "IMU_TEST";

static esp_err_t reg_read8(uint8_t reg, uint8_t *val)
{
    i2c_cmd_handle_t cmd = i2c_cmd_link_create();
    i2c_master_start(cmd);
    i2c_master_write_byte(cmd, (MPU_ADDR << 1) | I2C_MASTER_WRITE, true);
    i2c_master_write_byte(cmd, reg, true);
    i2c_master_start(cmd);
    i2c_master_write_byte(cmd, (MPU_ADDR << 1) | I2C_MASTER_READ, true);
    i2c_master_read_byte(cmd, val, I2C_MASTER_LAST_NACK);
    i2c_master_stop(cmd);
    esp_err_t err = i2c_master_cmd_begin(I2C_PORT, cmd, pdMS_TO_TICKS(100));
    i2c_cmd_link_delete(cmd);
    return err;
}

static esp_err_t reg_read_multi(uint8_t reg, uint8_t *buf, size_t n)
{
    i2c_cmd_handle_t cmd = i2c_cmd_link_create();
    i2c_master_start(cmd);
    i2c_master_write_byte(cmd, (MPU_ADDR << 1) | I2C_MASTER_WRITE, true);
    i2c_master_write_byte(cmd, reg, true);
    i2c_master_start(cmd);
    i2c_master_write_byte(cmd, (MPU_ADDR << 1) | I2C_MASTER_READ, true);
    if (n > 1) {
        i2c_master_read(cmd, buf, n - 1, I2C_MASTER_ACK);
    }
    i2c_master_read_byte(cmd, buf + n - 1, I2C_MASTER_LAST_NACK);
    i2c_master_stop(cmd);
    esp_err_t err = i2c_master_cmd_begin(I2C_PORT, cmd, pdMS_TO_TICKS(100));
    i2c_cmd_link_delete(cmd);
    return err;
}

static esp_err_t reg_write8(uint8_t reg, uint8_t val)
{
    i2c_cmd_handle_t cmd = i2c_cmd_link_create();
    i2c_master_start(cmd);
    i2c_master_write_byte(cmd, (MPU_ADDR << 1) | I2C_MASTER_WRITE, true);
    i2c_master_write_byte(cmd, reg, true);
    i2c_master_write_byte(cmd, val, true);
    i2c_master_stop(cmd);
    esp_err_t err = i2c_master_cmd_begin(I2C_PORT, cmd, pdMS_TO_TICKS(100));
    i2c_cmd_link_delete(cmd);
    return err;
}

static int16_t rd16(uint8_t *b)
{
    return (int16_t)((b[0] << 8) | b[1]);
}

void app_main(void)
{
    ESP_LOGI(TAG, "IMU standalone test - SDA=GPIO%d SCL=GPIO%d", SDA_PIN, SCL_PIN);

    i2c_config_t conf = {
        .mode = I2C_MODE_MASTER,
        .sda_io_num = SDA_PIN,
        .scl_io_num = SCL_PIN,
        .sda_pullup_en = GPIO_PULLUP_ENABLE,
        .scl_pullup_en = GPIO_PULLUP_ENABLE,
        .master.clk_speed = 400000,
    };
    ESP_ERROR_CHECK(i2c_param_config(I2C_PORT, &conf));
    ESP_ERROR_CHECK(i2c_driver_install(I2C_PORT, I2C_MODE_MASTER, 0, 0, 0));

    // I2C scan
    ESP_LOGI(TAG, "--- I2C bus scan ---");
    for (int addr = 0x08; addr < 0x78; addr++) {
        i2c_cmd_handle_t cmd = i2c_cmd_link_create();
        i2c_master_start(cmd);
        i2c_master_write_byte(cmd, (addr << 1) | I2C_MASTER_WRITE, true);
        i2c_master_stop(cmd);
        esp_err_t err = i2c_master_cmd_begin(I2C_PORT, cmd, pdMS_TO_TICKS(50));
        i2c_cmd_link_delete(cmd);
        if (err == ESP_OK) {
            ESP_LOGI(TAG, "  device found at 0x%02X", addr);
        }
    }

    uint8_t v;
    if (reg_read8(REG_WHO_AM_I, &v) != ESP_OK) {
        ESP_LOGE(TAG, "Cannot read WHO_AM_I! sensor not responding at 0x%02X", MPU_ADDR);
        vTaskDelay(pdMS_TO_TICKS(1000));
        return;
    }
    ESP_LOGI(TAG, "WHO_AM_I = 0x%02X", v);

    // Registers as-is
    uint8_t pwr1, pwr2, accel_cfg, gyro_cfg;
    reg_read8(REG_PWR_MGMT_1, &pwr1);
    reg_read8(REG_PWR_MGMT_2, &pwr2);
    reg_read8(REG_ACCEL_CONFIG, &accel_cfg);
    reg_read8(REG_GYRO_CONFIG, &gyro_cfg);
    ESP_LOGI(TAG, "PWR_MGMT_1=0x%02X (SLEEP=%d DEVICE_RESET=%d)", pwr1, (pwr1 >> 6) & 1, (pwr1 >> 7) & 1);
    ESP_LOGI(TAG, "PWR_MGMT_2=0x%02X (DIS_ACCEL bits: %d%d%d)", pwr2, (pwr2 >> 3) & 1, (pwr2 >> 4) & 1, (pwr2 >> 5) & 1);
    ESP_LOGI(TAG, "ACCEL_CONFIG=0x%02X (AFS=%d)  GYRO_CONFIG=0x%02X (FS=%d)", accel_cfg, (accel_cfg >> 3) & 3, gyro_cfg, (gyro_cfg >> 3) & 3);

    // Wake up (clear sleep)
    reg_write8(REG_PWR_MGMT_1, 0x00);
    vTaskDelay(pdMS_TO_TICKS(100));
    reg_read8(REG_PWR_MGMT_1, &pwr1);
    ESP_LOGI(TAG, "After wake: PWR_MGMT_1=0x%02X (SLEEP=%d)", pwr1, (pwr1 >> 6) & 1);

    // Read raw data 10 times
    ESP_LOGI(TAG, "--- raw accel / gyro / temp (10 samples) ---");
    uint8_t buf[14];
    for (int i = 0; i < 10; i++) {
        esp_err_t err = reg_read_multi(REG_ACCEL_XOUT_H, buf, 14);
        if (err != ESP_OK) {
            ESP_LOGE(TAG, "read failed err=%d", err);
            continue;
        }
        int16_t ax = rd16(&buf[0]), ay = rd16(&buf[2]), az = rd16(&buf[4]);
        int16_t temp = rd16(&buf[6]);
        int16_t gx = rd16(&buf[8]), gy = rd16(&buf[10]), gz = rd16(&buf[12]);
        ESP_LOGI(TAG, "sample %d: acc=(%6d,%6d,%6d) temp=%6d gyro=(%6d,%6d,%6d)",
                 i, ax, ay, az, temp, gx, gy, gz);
        vTaskDelay(pdMS_TO_TICKS(200));
    }

    ESP_LOGI(TAG, "--- done ---");
}
