#Requires -Version 5.1
<#
.SYNOPSIS
  把本仓库的 skills 以 NTFS junction 接入各 AI agent 的 skills 目录（统一真源，所有 agent 共用一份）。

.USAGE
  powershell -ExecutionPolicy Bypass -File install.ps1              # 用户级：zcode / agents / claude / codex
  powershell -ExecutionPolicy Bypass -File install.ps1 -Local       # 项目级：当前目录 .claude\skills 和 .agents\skills
  powershell -ExecutionPolicy Bypass -File install.ps1 -Remove      # 只移除指向本仓库的 junction
#>
param(
    [switch]$Local,
    [switch]$Remove
)
$ErrorActionPreference = 'Stop'
$RepoSkills = Join-Path $PSScriptRoot 'skills'
$BackupRoot = Join-Path $PSScriptRoot '.backup'

if ($Local) {
    $cwd = (Get-Location).Path
    $targets = [ordered]@{
        'claude(project)' = Join-Path $cwd '.claude\skills'
        'agents(project)' = Join-Path $cwd '.agents\skills'
    }
} else {
    $targets = [ordered]@{
        'zcode'  = Join-Path $env:USERPROFILE '.zcode\skills'
        'agents' = Join-Path $env:USERPROFILE '.agents\skills'
        'claude' = Join-Path $env:USERPROFILE '.claude\skills'
        'codex'  = Join-Path $env:USERPROFILE '.codex\skills'
    }
}

$skills = Get-ChildItem $RepoSkills -Directory
Write-Host ("Repo skills: {0}  ({1})" -f $skills.Count, $RepoSkills)

# 目录签名：相对路径 + 大小 + 修改时间，用于判断本地副本与仓库是否一致
function Get-DirSignature($dir) {
    Get-ChildItem $dir -Recurse -File -Force | ForEach-Object {
        $_.FullName.Substring($dir.Length + 1) + '|' + $_.Length + '|' + $_.LastWriteTimeUtc.Ticks
    } | Sort-Object
}

function Test-PointsToRepo($item) {
    $t = $item.Target
    if (-not $t) { return $false }
    if ($t -is [array]) { $t = $t[0] }
    return ($t -and (([string]$t).StartsWith($RepoSkills, [StringComparison]::OrdinalIgnoreCase)))
}

foreach ($agent in $targets.Keys) {
    $root = $targets[$agent]
    if (-not (Test-Path $root)) { New-Item -ItemType Directory -Force -Path $root | Out-Null }
    Write-Host "`n=== $agent -> $root ==="

    foreach ($skill in $skills) {
        $dest = Join-Path $root $skill.Name

        if ($Remove) {
            if (Test-Path $dest) {
                $item = Get-Item $dest -Force
                if ($item.LinkType -eq 'Junction' -and (Test-PointsToRepo $item)) {
                    $item.Delete()
                    Write-Host "  removed  $($skill.Name)"
                }
            }
            continue
        }

        if (Test-Path $dest) {
            $item = Get-Item $dest -Force
            if ($item.LinkType -eq 'Junction') {
                if (Test-PointsToRepo $item) { continue }               # 已接入，跳过
                $item.Delete()                                          # 指向别处的旧链接，重建
                Write-Host "  relink   $($skill.Name) (旧 junction 指向别处)"
            } else {
                # 真实目录：与仓库一致则直接替换，不一致先备份
                $same = $false
                try { $same = ((Compare-Object (Get-DirSignature $dest) (Get-DirSignature $skill.FullName)) -eq $null) } catch {}
                if (-not $same) {
                    $stamp = Get-Date -Format 'yyyyMMdd-HHmmss'
                    $bak = Join-Path (Join-Path $BackupRoot $stamp) $agent
                    New-Item -ItemType Directory -Force -Path $bak | Out-Null
                    Move-Item $dest (Join-Path $bak $skill.Name)
                    Write-Host "  backup   $($skill.Name) -> .backup\$stamp\$agent\"
                } else {
                    Remove-Item $dest -Recurse -Force
                }
            }
        }
        New-Item -ItemType Junction -Path $dest -Target $skill.FullName | Out-Null
        if (-not ($item -and $item.LinkType -eq 'Junction')) { Write-Host "  linked   $($skill.Name)" }
    }
}

if ($Remove) { Write-Host "`nDone (removed)." } else { Write-Host "`nDone. 所有 agent 的 skills 目录已指向本仓库（唯一真源）。" }
