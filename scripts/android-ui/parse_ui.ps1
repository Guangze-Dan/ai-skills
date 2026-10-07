$c = Get-Content 'D:\Zcode\tools\ui.xml' -Raw
$m = [regex]::Matches($c, 'resource-id="([^"]*)"[^>]*?bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"')
foreach ($x in $m) {
    Write-Host ($x.Groups[1].Value + ' @ ' + $x.Groups[2].Value + ',' + $x.Groups[3].Value + ' -> ' + $x.Groups[4].Value + ',' + $x.Groups[5].Value)
}
$t = [regex]::Matches($c, 'text="([^"]+)"[^>]*?bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"')
foreach ($x in $t) {
    Write-Host ('TEXT[' + $x.Groups[1].Value + '] @ ' + $x.Groups[2].Value + ',' + $x.Groups[3].Value + ' -> ' + $x.Groups[4].Value + ',' + $x.Groups[5].Value)
}
