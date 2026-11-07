import serial
import time
import sys

print("Opening COM8...")
ser = serial.Serial()
ser.port = 'COM8'
ser.baudrate = 115200
ser.timeout = 1
ser.dtr = False
ser.rts = False
ser.open()

# Read until boot/AP starts or up to 25 seconds
print("Waiting for ESP32 to reach ready state...")
start = time.time()
while time.time() - start < 25:
    if ser.in_waiting:
        line = ser.readline().decode('utf-8', errors='replace').strip()
        if line:
            print(f"[{time.strftime('%H:%M:%S')}] {line}")
            if "HTTP server started" in line or "Access Point started" in line:
                print("ESP32 is READY!")
                break
    time.sleep(0.05)

print("\n>>> SENDING HARDWARE SELF-TEST COMMAND ('TEST_ALL') <<<")
time.sleep(1)
ser.write(b"TEST_ALL\n")

# Collect output from self-test for 15 seconds
start = time.time()
while time.time() - start < 15:
    if ser.in_waiting:
        line = ser.readline().decode('utf-8', errors='replace').strip()
        if line:
            print(f"[{time.strftime('%H:%M:%S')}] {line}")
            if "ALL OFF" in line:
                break
    time.sleep(0.05)

print("\n>>> SENDING SENSOR STATUS QUERY ('STATUS') <<<")
ser.write(b"STATUS\n")
time.sleep(0.5)
while ser.in_waiting:
    line = ser.readline().decode('utf-8', errors='replace').strip()
    if line:
        print(f"[{time.strftime('%H:%M:%S')}] {line}")

ser.close()
print("\n>>> TEST SCRIPT FINISHED <<<")

