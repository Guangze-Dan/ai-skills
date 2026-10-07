#Requires -Version 5.1
# 扫描 skills/*/SKILL.md 的 YAML frontmatter，重建 registry.json
$ErrorActionPreference = 'Stop'
$RepoSkills = Join-Path $PSScriptRoot '..\skills'
$outPath = Join-Path $PSScriptRoot '..\registry.json'

function Parse-Frontmatter($path) {
    $raw = [IO.File]::ReadAllText($path, [Text.Encoding]::UTF8)
    $m = [regex]::Match($raw, '(?s)^---\r?\n(.*?)\r?\n---')
    if (-not $m.Success) { return $null }
    $fm = $m.Groups[1].Value

    $name = ''
    $nm = [regex]::Match($fm, '(?m)^name:[ \t]*(.+)$')
    if ($nm.Success) { $name = $nm.Groups[1].Value.Trim().Trim('"').Trim("'") }

    $desc = ''
    $block = [regex]::Match($fm, '(?ms)^description:[ \t]*(?:[>|][+-]?)[ \t]*\r?\n((?:[ \t]+.*\r?\n?)+)')
    if ($block.Success) {
        $desc = (($block.Groups[1].Value -split "\r?\n") | ForEach-Object { $_.Trim() }) -join ' '
    } else {
        $inline = [regex]::Match($fm, '(?m)^description:[ \t]*(.+)$')
        if ($inline.Success) { $desc = $inline.Groups[1].Value.Trim() }
        if ($desc.StartsWith('"') -and $desc.EndsWith('"') -and $desc.Length -ge 2) { $desc = $desc.Substring(1, $desc.Length - 2) }
        if ($desc.StartsWith("'") -and $desc.EndsWith("'") -and $desc.Length -ge 2) { $desc = $desc.Substring(1, $desc.Length - 2) }
    }
    return @{ name = $name; description = $desc }
}

$entries = @()
foreach ($dir in (Get-ChildItem $RepoSkills -Directory | Sort-Object Name)) {
    $skillMd = Join-Path $dir.FullName 'SKILL.md'
    if (-not (Test-Path $skillMd)) { continue }
    $fm = Parse-Frontmatter $skillMd
    $entries += [ordered]@{
        name        = if ($fm -and $fm.name) { $fm.name } else { $dir.Name }
        dir         = 'skills/' + $dir.Name
        description = if ($fm) { $fm.description } else { '' }
    }
}

$doc = [ordered]@{
    updated = (Get-Date).ToString('yyyy-MM-dd')
    source  = 'https://github.com/Guangze-Dan/ai-skills'
    count   = $entries.Count
    skills  = $entries
}
$json = ConvertTo-Json $doc -Depth 5
[IO.File]::WriteAllText($outPath, $json, (New-Object Text.UTF8Encoding $false))
Write-Host ("registry.json rebuilt: {0} skills" -f $entries.Count)
