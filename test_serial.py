import serial
import time

ser = serial.Serial()
ser.port = 'COM8'
ser.baudrate = 115200
ser.timeout = 1
ser.dtr = False
ser.rts = False
ser.open()

print("--- ESP32 LOGS START (35s) ---")
start = time.time()
while time.time() - start < 35:
    if ser.in_waiting:
        line = ser.readline().decode('utf-8', errors='replace').strip()
        if line:
            timestamp = time.strftime("%H:%M:%S")
            print(f"[{timestamp}] {line}")
    time.sleep(0.01)

print("--- ESP32 LOGS END ---")
ser.close()
