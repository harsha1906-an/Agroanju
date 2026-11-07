import subprocess
import time
import sys

bin_path = r"D:\Documents\agro\esp32\mainesp_code\build\mainesp_code.ino.merged.bin"

print("=" * 60)
print(">>> FLASHING AGRO-VATORS FIRMWARE TO ESP32 (COM8) <<<")
print("NOTE: 1. Disconnect motor battery power completely!")
print("      2. If you see 'Connecting...', press and hold BOOT.")
print("=" * 60)

cmd = [
    sys.executable, "-m", "esptool",
    "--port", "COM8",
    "--baud", "115200",
    "--before", "default-reset",
    "--after", "hard-reset",
    "write-flash",
    "-z",
    "--flash-mode", "dio",
    "--flash-freq", "80m",
    "--flash-size", "4MB",
    "0x0", bin_path
]

res = subprocess.run(cmd)
if res.returncode == 0:
    print("\nSUCCESS! Firmware flashed successfully!")
else:
    print(f"\nUpload exited with code {res.returncode}")
