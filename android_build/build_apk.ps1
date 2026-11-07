$ErrorActionPreference = "Stop"

$sdk = "$env:LOCALAPPDATA\Android\Sdk"
$buildTools = "$sdk\build-tools\35.0.0"
$platform = "$sdk\platforms\android-34"
$jdkBin = "C:\Program Files\Android\Android Studio\jbr\bin"

Write-Host ">>> Cleaning build artifacts..."
Remove-Item -Recurse -Force -ErrorAction SilentlyContinue "android_build\obj", "android_build\dex"
New-Item -ItemType Directory -Force -Path "android_build\obj", "android_build\dex", "android_build\dist" | Out-Null

Write-Host ">>> Step 1: Compiling Android Resources with aapt2..."
& "$buildTools\aapt2.exe" compile --dir android_app\res -o android_build\compiled_res.zip

Write-Host ">>> Step 2: Linking APK package and generating R.java..."
& "$buildTools\aapt2.exe" link -I "$platform\android.jar" `
    --manifest android_app\AndroidManifest.xml `
    -A android_app\assets `
    -o android_build\app-unaligned.apk `
    --java android_app\src `
    android_build\compiled_res.zip `
    --auto-add-overlay

Write-Host ">>> Step 3: Compiling Java Sources with javac (Android Studio JBR)..."
$javaFiles = Get-ChildItem "android_app\src\com\agrovators\agrirover\*.java" | ForEach-Object { $_.FullName }
& "$jdkBin\javac.exe" --release 8 -cp "$platform\android.jar" -d android_build\obj $javaFiles

Write-Host ">>> Step 4: Dexing class files with d8..."
$classFiles = Get-ChildItem "android_build\obj\com\agrovators\agrirover\*.class" | ForEach-Object { $_.FullName }
& "$buildTools\d8.bat" --output android_build\dex --lib "$platform\android.jar" $classFiles

Write-Host ">>> Step 5: Adding classes.dex to APK package..."
Set-Location android_build\dex
& "$jdkBin\jar.exe" -uf "..\app-unaligned.apk" classes.dex
Set-Location ..\..

Write-Host ">>> Step 6: Aligning APK with zipalign..."
& "$buildTools\zipalign.exe" -f -p 4 android_build\app-unaligned.apk android_build\app-aligned.apk

Write-Host ">>> Step 7: Signing APK with apksigner..."
$keystore = "android_build\debug.keystore"
if (-not (Test-Path $keystore)) {
    Write-Host "Generating debug keystore..."
    & "$jdkBin\keytool.exe" -genkey -v -keystore $keystore -storepass android -alias androiddebugkey -keypass android -keyalg RSA -keysize 2048 -validity 10000 -dname "CN=AgriRover,O=AgroVators,C=IN"
}

& "$buildTools\apksigner.bat" sign --ks $keystore --ks-pass pass:android --ks-key-alias androiddebugkey --key-pass pass:android --out android_build\dist\AgriRover.apk android_build\app-aligned.apk

Write-Host ">>> Step 8: Verifying signed APK..."
& "$buildTools\apksigner.bat" verify android_build\dist\AgriRover.apk

$finalApk = Get-Item "android_build\dist\AgriRover.apk"
Write-Host ">>> SUCCESS! APK generated at: $($finalApk.FullName) ($([math]::Round($finalApk.Length / 1KB, 1)) KB)"
