$c = Get-Content 'D:\Zcode\aw2.txt' -Raw
$lines = $c -split "`n"
$inWidget = $false
foreach ($ln in $lines) {
    if ($ln -match 'id=481') { $inWidget = $true }
    if ($inWidget) {
        Write-Output $ln.TrimEnd()
        if ($ln -match '^\s*\[\d+\] id=' -and $ln -notmatch 'id=481') { break }
    }
}
