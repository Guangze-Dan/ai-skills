#Requires -Version 5.1
<#
.SYNOPSIS
  Link every skill in this repo into each AI agent's skills directory via NTFS junction.
  The repo stays the single source of truth; all agents read the same files.

.USAGE
  powershell -ExecutionPolicy Bypass -File install.ps1              # user level: zcode / agents / claude / codex
  powershell -ExecutionPolicy Bypass -File install.ps1 -Local       # project level: .claude\skills and .agents\skills in cwd
  powershell -ExecutionPolicy Bypass -File install.ps1 -Remove      # remove only junctions pointing into this repo
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

# Directory signature: relative path + size + mtime, used to compare a local copy with the repo copy
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
                if (Test-PointsToRepo $item) { continue }               # already linked
                $item.Delete()                                          # stale junction elsewhere, recreate
                Write-Host "  relink   $($skill.Name) (old junction pointed elsewhere)"
            } else {
                # Real directory: identical to repo -> replace directly, otherwise back it up first
                $same = $false
                try { $same = ((Compare-Object (Get-DirSignature $dest) (Get-DirSignature $skill.FullName)) -eq $null) } catch {}
                if (-not $same) {
                    $stamp = Get-Date -Format 'yyyyMMdd-HHmmss'
                    $bak = Join-Path (Join-Path $BackupRoot $stamp) $agent
                    New-Item -ItemType Directory -Force -Path $bak | Out-Null
                    try {
                        Move-Item $dest (Join-Path $bak $skill.Name) -ErrorAction Stop
                        Write-Host "  backup   $($skill.Name) -> .backup\$stamp\$agent\"
                    } catch {
                        Write-Host ("  SKIP     {0} (in use: {1})" -f $skill.Name, $_.Exception.Message)
                        continue
                    }
                } else {
                    try { Remove-Item $dest -Recurse -Force -ErrorAction Stop } catch {
                        Write-Host ("  SKIP     {0} (in use; re-run install.ps1 later to finish)" -f $skill.Name)
                        continue
                    }
                }
            }
        }
        try {
            New-Item -ItemType Junction -Path $dest -Target $skill.FullName -ErrorAction Stop | Out-Null
            Write-Host "  linked   $($skill.Name)"
        } catch {
            Write-Host ("  SKIP     {0} (junction failed: {1})" -f $skill.Name, $_.Exception.Message)
        }
    }
}

if ($Remove) { Write-Host "`nDone (removed)." } else { Write-Host "`nDone. All agent skill dirs now point to this repo (single source of truth)." }
