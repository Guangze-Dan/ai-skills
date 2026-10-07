# 用Windows内置MTP驱动修复WPD设备
$instanceId = "USB\VID_2717&PID_FF48&MI_00\6&1BCA9814&0&0000"
$mtpInf = "C:\Windows\INF\wpdmtp.inf"

Write-Host "Installing built-in MTP driver for: $instanceId"
Write-Host "MTP inf exists: $(Test-Path $mtpInf)"

$proc = Start-Process pnputil -ArgumentList "/update-driver `"$instanceId`" `"$mtpInf`"" -Verb RunAs -Wait -PassThru
Write-Host "MTP driver update exit code: $($proc.ExitCode)"

Start-Sleep -Seconds 2

Write-Host "`nDevice status after update:"
Get-PnpDevice | Where-Object {$_.InstanceId -match 'VID_2717'} | Select-Object Status, Class, FriendlyName | Format-Table -AutoSize