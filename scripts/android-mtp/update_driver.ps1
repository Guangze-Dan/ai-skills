$instanceId = "USB\VID_2717&PID_FF48&MI_01\6&1BCA9814&0&0001"
$infPath = "C:\android-env\sdk\extras\google\usb_driver\android_winusb.inf"

Write-Host "Updating driver for: $instanceId"
$proc = Start-Process pnputil -ArgumentList "/update-driver `"$instanceId`" `"$infPath`"" -Verb RunAs -Wait -PassThru
Write-Host "Exit code: $($proc.ExitCode)"

Start-Sleep -Seconds 2

$device = Get-PnpDevice | Where-Object {$_.FriendlyName -match 'ADB|Android|Xiaomi'}
$device | Select-Object Status, Class, FriendlyName | Format-Table -AutoSize