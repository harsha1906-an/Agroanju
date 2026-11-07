import subprocess
import sys

bin_path = r"d:\Documents\agro\esp32\CameraWebServer\build\CameraWebServer.ino.merged.bin"

print("=" * 60)
print(">>> FLASHING ESP32-CAM FIRMWARE <<<")
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
    print("\nSUCCESS! Camera flashed successfully!")
    print("Now unplug the wires and remove IO0 from GND.")
else:
    print(f"\nUpload exited with code {res.returncode}")

