#Requires -Version 5.1
# Auto-sync task scripts into the ai-skills repo. Called by ZCode hooks
# (UserPromptSubmit + Stop) so any script produced during a task lands in
# GitHub automatically. Idempotent, quiet, always exits 0.
#
# Watch scope: root-level script files (non-recursive) of $WatchRoots.
#   - first-seen file  -> scripts/inbox/<yyyy-MM-dd>/<name>   (import + git push)
#   - changed file     -> same repo destination as before     (import + git push)
#   - unchanged        -> nothing happens (fast no-op)
# Add more paths to $WatchRoots to widen coverage.

$ErrorActionPreference = 'Stop'

$Repo       = Split-Path -Parent $PSScriptRoot   # repo root = parent of this tools\ dir
$StateFile  = Join-Path $Repo 'tools\.sync-state.json'
$LogFile    = Join-Path $Repo 'tools\sync.log'
# Watch roots are machine-specific; missing paths are skipped automatically.
$WatchRoots = @(
    'E:\Zcode数据\.zcode\workspace\default',
    'E:\Zcode数据'
)
$Extensions = @('.ps1', '.py', '.bat', '.cmd', '.sh', '.js', '.ts', '.ahk')
$MaxBytes   = 2MB

# Scripts already collected before auto-sync existed: filename -> repo-relative path.
# Keeps future edits of these files updating the same repo destination.
$SeedMap = @{
    'copy_apk.ps1'                     = 'scripts/android-mtp/copy_apk.ps1'
    'fix_mtp_driver.ps1'               = 'scripts/android-mtp/fix_mtp_driver.ps1'
    'reenumerate.ps1'                  = 'scripts/android-mtp/reenumerate.ps1'
    'update_driver.ps1'                = 'scripts/android-mtp/update_driver.ps1'
    'read_schedule.py'                 = 'scripts/productivity/read_schedule.py'
    'ui_mockup.py'                     = 'scripts/productivity/ui_mockup.py'
    'dump481.ps1'                      = 'scripts/android-ui/dump481.ps1'
    '_check.py'                        = 'scripts/legacy/check_files.py'
    '_explore.py'                      = 'scripts/legacy/explore_tree.py'
    '启动ZCode.bat'                    = 'scripts/productivity/start_zcode.bat'
    '_C盘收尾_关闭ZCode后运行.bat'     = 'scripts/legacy/c_drive_cleanup.bat'
}

try {
    # ---- load state: $files is a plain hashtable { source-path-lc: {hash, dest} }
    $files = @{}
    $baselined = $false
    if (Test-Path $StateFile) {
        try {
            $loaded = Get-Content $StateFile -Raw -Encoding UTF8 | ConvertFrom-Json
            if ($loaded.files) {
                foreach ($p in $loaded.files.PSObject.Properties) { $files[$p.Name] = $p.Value }
            }
            $baselined = [bool]$loaded.baselined
        } catch { $files = @{} }
    }
    $seeding = -not $baselined   # first run: baseline only, import nothing

    $Git = 'C:\Program Files\Git\cmd\git.exe'
    if (-not (Test-Path $Git)) { $Git = 'git' }

    # Native git can print warnings to stderr; under Stop preference that throws.
    # Run it with Continue preference and merge streams instead.
    function Invoke-Git {
        param([Parameter(ValueFromRemainingArguments = $true)][string[]]$GitArgs)
        $prev = $ErrorActionPreference
        $ErrorActionPreference = 'Continue'
        try { return (& $Git -C $Repo @GitArgs 2>&1) } finally { $ErrorActionPreference = $prev }
    }
    function Get-FileHash2($p) { (Get-FileHash -LiteralPath $p -Algorithm SHA256).Hash }

    function New-InboxDest($f) {
        $stamp = Get-Date -Format 'yyyy-MM-dd'
        $srch  = Get-FileHash2 $f.FullName
        $base  = "scripts/inbox/$stamp/$($f.BaseName)"
        $cand  = "$base$($f.Extension)"; $i = 2
        while ($true) {
            $full = Join-Path $Repo ($cand -replace '/', '\')
            if (-not (Test-Path $full)) { return $cand }
            try { if ((Get-FileHash2 $full) -eq $srch) { return $cand } } catch {}   # crash recovery: same content already staged
            $cand = "$base-$i$($f.Extension)"; $i++
        }
    }

    # ---- scan watch roots (non-recursive) ----------------------------------
    $imports = New-Object System.Collections.Generic.List[object]
    foreach ($root in $WatchRoots) {
        if (-not (Test-Path $root)) { continue }
        foreach ($f in (Get-ChildItem -LiteralPath $root -File -ErrorAction SilentlyContinue)) {
            if ($Extensions -notcontains $f.Extension.ToLower()) { continue }
            if ($f.Length -gt $MaxBytes) { continue }

            $key  = $f.FullName.ToLower()
            $hash = Get-FileHash2 $f.FullName

            if ($files.ContainsKey($key)) {
                $e = $files[$key]
                if ($e.hash -ne $hash) {
                    $dest = $e.dest
                    if (-not $dest) { $dest = New-InboxDest $f }        # changed + no dest yet -> inbox
                    $imports.Add([pscustomobject]@{ src = $f.FullName; dest = $dest })
                    $files[$key] = [pscustomobject]@{ hash = $hash; dest = $dest }
                }
            } else {
                $dest = $null
                if ($SeedMap.ContainsKey($f.Name)) {
                    $dest = $SeedMap[$f.Name]                           # pre-existing mapping, no import
                } elseif (-not $seeding) {
                    $dest = New-InboxDest $f                            # new task script -> import
                    $imports.Add([pscustomobject]@{ src = $f.FullName; dest = $dest })
                }
                $files[$key] = [pscustomobject]@{ hash = $hash; dest = $dest }
            }
        }
    }

    # ---- import changed/new files ------------------------------------------
    foreach ($m in $imports) {
        $destFull = Join-Path $Repo ($m.dest -replace '/', '\')
        New-Item -ItemType Directory -Force -Path (Split-Path $destFull) | Out-Null
        Copy-Item -LiteralPath $m.src -Destination $destFull -Force
    }

    # ---- git commit + push when there is something to push -----------------
    $committed = $false; $pushed = $false
    if ($imports.Count -gt 0) {
        Invoke-Git add -A -- scripts | Out-Null
        $dirty = (Invoke-Git status --porcelain) -join ''
        if ($dirty) {
            $msg = "auto-sync: {0} task script(s) ({1})" -f $imports.Count, (Get-Date -Format 'yyyy-MM-dd HH:mm')
            Invoke-Git commit -m $msg | Out-Null
            if ($LASTEXITCODE -eq 0) { $committed = $true }
        }
    }
    $ahead = Invoke-Git rev-list --count 'origin/main..HEAD' | Select-Object -First 1
    if ("$ahead" -match '^\d+$' -and [int]$ahead -gt 0) {
        Invoke-Git push | Out-Null
        if ($LASTEXITCODE -eq 0) { $pushed = $true }
    }

    # ---- persist state + log ----------------------------------------------
    [pscustomobject]@{ baselined = $true; files = $files } | ConvertTo-Json -Depth 6 | Out-File $StateFile -Encoding utf8
    $line = "{0} | tracked={1} imported={2} committed={3} pushed={4}" -f (Get-Date -Format 'yyyy-MM-dd HH:mm:ss'), $files.Count, $imports.Count, $committed, $pushed
    Add-Content -LiteralPath $LogFile -Value $line -Encoding UTF8
} catch {
    try { Add-Content -LiteralPath $LogFile -Value ("{0} | ERROR {1}" -f (Get-Date -Format 'yyyy-MM-dd HH:mm:ss'), $_.Exception.Message) -Encoding UTF8 } catch {}
}
exit 0
