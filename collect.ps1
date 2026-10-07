#Requires -Version 5.1
<#
.SYNOPSIS
  反向收集：把各 agent 目录里新增/修改的 skill 收进本仓库（唯一真源），并重建 registry.json。
  之后在仓库里 git push 即可同步到 GitHub。

.USAGE
  powershell -ExecutionPolicy Bypass -File collect.ps1          # 收集 + 更新 registry.json
  powershell -ExecutionPolicy Bypass -File collect.ps1 -Push    # 收集后自动 git commit + push
#>
param([switch]$Push)
$ErrorActionPreference = 'Stop'
$RepoSkills = Join-Path $PSScriptRoot 'skills'
$Sources = @(
    (Join-Path $env:USERPROFILE '.zcode\skills'),
    (Join-Path $env:USERPROFILE '.agents\skills'),
    (Join-Path $env:USERPROFILE '.claude\skills'),
    (Join-Path $env:USERPROFILE '.codex\skills')
)

function Get-DirSignature($dir) {
    Get-ChildItem $dir -Recurse -File -Force | ForEach-Object {
        $_.FullName.Substring($dir.Length + 1) + '|' + $_.Length + '|' + $_.LastWriteTimeUtc.Ticks
    } | Sort-Object
}

$seen = @{}
$added = 0; $updated = 0; $relinked = 0

foreach ($src in $Sources) {
    if (-not (Test-Path $src)) { continue }
    foreach ($dir in (Get-ChildItem $src -Directory)) {
        if ($dir.Name -eq '.system' -or $seen.ContainsKey($dir.Name)) { continue }

        $item = Get-Item $dir.FullName -Force
        if ($item.LinkType -eq 'Junction') {
            $t = $item.Target; if ($t -is [array]) { $t = $t[0] }
            if ($t -and (([string]$t).StartsWith($RepoSkills, [StringComparison]::OrdinalIgnoreCase))) { continue }  # 已是真源 junction
            $item.Delete(); New-Item -ItemType Junction -Path $dir.FullName -Target (Join-Path $RepoSkills $dir.Name) | Out-Null
            $seen[$dir.Name] = $true; $relinked++; continue
        }

        $repoDir = Join-Path $RepoSkills $dir.Name
        if (Test-Path $repoDir) {
            $same = $false
            try { $same = ((Compare-Object (Get-DirSignature $dir.FullName) (Get-DirSignature $repoDir)) -eq $null) } catch {}
            if ($same) {
                Remove-Item -LiteralPath $dir.FullName -Recurse -Force; New-Item -ItemType Junction -Path $dir.FullName -Target $repoDir | Out-Null
                $seen[$dir.Name] = $true; $relinked++
                Write-Host ("  unchanged -> relinked  " + $dir.Name)
                continue
            }
            Copy-Item (Join-Path $dir.FullName '*') $repoDir -Recurse -Force
            Write-Host ("  updated   " + $dir.Name)
            Remove-Item -LiteralPath $dir.FullName -Recurse -Force; New-Item -ItemType Junction -Path $dir.FullName -Target $repoDir | Out-Null
            $updated++
        } else {
            Copy-Item $dir.FullName $repoDir -Recurse
            Write-Host ("  added     " + $dir.Name)
            Remove-Item -LiteralPath $dir.FullName -Recurse -Force; New-Item -ItemType Junction -Path $dir.FullName -Target $repoDir | Out-Null
            $added++
        }
        $seen[$dir.Name] = $true
    }
}

Write-Host ("`nCollect done: added={0} updated={1} relinked={2}" -f $added, $updated, $relinked)

# 重建 registry.json
& (Join-Path $PSScriptRoot 'tools\gen_registry.ps1')

if ($Push) {
    git -C $PSScriptRoot add -A
    $msg = "collect: sync skills from local agents ($((Get-Date).ToString('yyyy-MM-dd HH:mm')))"
    $hasChanges = git -C $PSScriptRoot status --porcelain
    if ($hasChanges) {
        git -C $PSScriptRoot commit -m $msg
        git -C $PSScriptRoot push
        Write-Host "Pushed to GitHub."
    } else {
        Write-Host "No changes to commit."
    }
}
