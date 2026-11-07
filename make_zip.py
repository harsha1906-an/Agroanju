import os
import zipfile
import time

zip_path = r"D:\Documents\agro\AGRO-VATORS_Package.zip"
base_dir = r"D:\Documents\agro"

if os.path.exists(zip_path):
    os.remove(zip_path)

exclude_dirs = {
    ".git", "venv", ".venv", "__pycache__", ".idea", ".vscode"
}
exclude_extensions = {
    ".pyc", ".map", ".elf"
}
exclude_prefixes = (
    "test_", "check_", "phone_screen", "live_dashboard_frame"
)

files_to_zip = []

for root, dirs, files in os.walk(base_dir):
    # Prune excluded directories
    dirs[:] = [d for d in dirs if d not in exclude_dirs and not d.startswith(".")]

    # Also skip android_build intermediate obj/dex
    if "android_build" in root and ("obj" in root or "dex" in root):
        continue

    for f in files:
        if f == "AGRO-VATORS_Package.zip":
            continue
        ext = os.path.splitext(f)[1].lower()
        if ext in exclude_extensions:
            continue
        if any(f.startswith(p) for p in exclude_prefixes):
            continue
        full_path = os.path.join(root, f)
        rel_path = os.path.relpath(full_path, base_dir)
        files_to_zip.append((full_path, rel_path))

print(f"Archiving {len(files_to_zip)} files into {zip_path}...")

with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as zipf:
    for full_path, rel_path in files_to_zip:
        zipf.write(full_path, rel_path)

size_mb = os.path.getsize(zip_path) / (1024 * 1024)
print(f"\n>>> SUCCESS! Created {zip_path} ({size_mb:.2f} MB)")

