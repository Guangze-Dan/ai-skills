$apkSource = "C:\机械硬盘\Zcode\.zcode\workspace\default\StudentScheduleWidget\app\build\outputs\apk\debug\app-debug.apk"

Write-Host "APK source: $apkSource"
Write-Host "APK exists: $(Test-Path $apkSource)"

# 通过 Shell.Application 访问 MTP 设备
$shell = New-Object -ComObject Shell.Application
$computer = $shell.NameSpace(17)  # 17 = My Computer

Write-Host "`nLooking for phone..."
$phone = $null
foreach ($item in $computer.Items()) {
    Write-Host "  Found device: $($item.Name)"
    if ($item.Name -match 'Xiaomi|17 Pro|MI ') {
        $phone = $item
        break
    }
}

if ($phone -eq $null) {
    Write-Host "`nPhone not found via MTP. Devices listed above."
    exit 1
}

Write-Host "`nPhone found: $($phone.Name)"
$phoneFolder = $phone.GetFolder
Write-Host "Phone storage items:"
foreach ($sub in $phoneFolder.Items()) {
    Write-Host "  - $($sub.Name)"
}

# 进入内部存储
$internal = $null
foreach ($sub in $phoneFolder.Items()) {
    if ($sub.Name -match '内部|Internal|storage') {
        $internal = $sub
        break
    }
}
if ($internal -eq $null) { $internal = $phoneFolder.Items() | Select-Object -First 1 }

Write-Host "`nUsing storage: $($internal.Name)"
$internalFolder = $internal.GetFolder

# 找 Download 文件夹
$download = $null
foreach ($sub in $internalFolder.Items()) {
    if ($sub.Name -match 'Download|下载') {
        $download = $sub
        break
    }
}

if ($download -eq $null) {
    Write-Host "Download folder not found, copying to root..."
    $targetFolder = $internalFolder
} else {
    Write-Host "Download folder found: $($download.Name)"
    $targetFolder = $download.GetFolder
}

# 复制 APK
Write-Host "`nCopying APK to phone..."
$targetFolder.CopyHere($apkSource, 16)
Write-Host "Copy initiated. Waiting for transfer..."
Start-Sleep -Seconds 8
Write-Host "Done! Check phone's Download folder."