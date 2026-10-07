# 强制重新枚举小米USB设备
Write-Host "Finding Xiaomi USB devices..."
$devices = Get-PnpDevice | Where-Object {$_.InstanceId -match 'VID_2717'}

foreach ($d in $devices) {
    Write-Host "  $($d.InstanceId) - $($d.FriendlyName) [$($d.Status)]"
}

$script = {
    param($ids)
    foreach ($id in $ids) {
        try {
            Disable-PnpDevice -InstanceId $id -Confirm:$false -ErrorAction Stop
            Write-Host "Disabled: $id"
        } catch {
            Write-Host "Disable failed: $id - $($_.Exception.Message)"
        }
    }
    Start-Sleep -Seconds 2
    foreach ($id in $ids) {
        try {
            Enable-PnpDevice -InstanceId $id -Confirm:$false -ErrorAction Stop
            Write-Host "Enabled: $id"
        } catch {
            Write-Host "Enable failed: $id - $($_.Exception.Message)"
        }
    }
}

$ids = $devices | ForEach-Object { $_.InstanceId }
$idsText = $ids -join ';'

Start-Process powershell -ArgumentList "-NoProfile -ExecutionPolicy Bypass -Command `"& { `$ids = '$idsText' -split ';'; foreach (`$id in `$ids) { try { Disable-PnpDevice -InstanceId `$id -Confirm:`$false -ErrorAction Stop } catch {}; Start-Sleep -Seconds 2; foreach (`$id in `$ids) { try { Enable-PnpDevice -InstanceId `$id -Confirm:`$false -ErrorAction Stop } catch {} } }`"" -Verb RunAs -Wait

Start-Sleep -Seconds 3
Write-Host "`nAfter re-enumeration:"
Get-PnpDevice | Where-Object {$_.InstanceId -match 'VID_2717'} | Select-Object Status, Class, FriendlyName | Format-Table -AutoSize