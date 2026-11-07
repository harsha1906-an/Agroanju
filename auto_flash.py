import serial
import subprocess
import time
import sys

bin_path = r"C:\Users\Harsha\AppData\Local\arduino\sketches\F217F49F3AB3623C9A55652DD1A23A68\mainesp_code.ino.merged.bin"
port = "COM8"

def flash():
    print("\n>>> STARTING ESPTOOL WRITE FLASH <<<")
    cmd = [
        sys.executable, "-m", "esptool",
        "--port", port,
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
    return res.returncode == 0

if __name__ == "__main__":
    flash()

