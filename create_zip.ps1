$ErrorActionPreference = "Stop"

$zipFile = "D:\Documents\agro\AGRO-VATORS_Package.zip"
if (Test-Path $zipFile) {
    Remove-Item -Force $zipFile
}

$excludePatterns = @(
    "*\.git\*",
    "*\venv\*",
    "*\__pycache__\*",
    "*\*.pyc",
    "*\android_build\obj\*",
    "*\android_build\dex\*",
    "*\*.map",
    "*\*.elf",
    "*\test_*.jpg",
    "*\check_*.jpg",
    "*\phone_screen*.png",
    "*\live_dashboard_frame.jpg"
)

$baseDir = "D:\Documents\agro\"

$allFiles = Get-ChildItem -Path $baseDir -Recurse -File | Where-Object {
    $filePath = $_.FullName
    $excluded = $false
    foreach ($pat in $excludePatterns) {
        if ($filePath -like $pat) {
            $excluded = $true
            break
        }
    }
    -not $excluded
}

Write-Host "Archiving $($allFiles.Count) files into package..."

Add-Type -AssemblyName System.IO.Compression.FileSystem
$zip = [System.IO.Compression.ZipFile]::Open($zipFile, [System.IO.Compression.ZipArchiveMode]::Create)

foreach ($f in $allFiles) {
    $relative = $f.FullName.Substring($baseDir.Length).Replace("\", "/")
    [System.IO.Compression.ZipFileExtensions]::CreateEntryFromFile($zip, $f.FullName, $relative, [System.IO.Compression.CompressionLevel]::Optimal) | Out-Null
}

$zip.Dispose()

$zipItem = Get-Item $zipFile
$sizeMB = [math]::Round($zipItem.Length / 1MB, 2)
Write-Host ">>> SUCCESS! Created $zipFile ($sizeMB MB)"

