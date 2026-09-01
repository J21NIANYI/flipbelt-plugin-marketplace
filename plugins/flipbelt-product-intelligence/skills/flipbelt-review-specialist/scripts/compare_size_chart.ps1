[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$Reference,

    [Parameter(Mandatory = $true)]
    [string]$Target
)

$ErrorActionPreference = 'Stop'
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

if (-not (Test-Path -LiteralPath $Reference)) {
    throw "Reference file not found: $Reference"
}
if (-not (Test-Path -LiteralPath $Target)) {
    throw "Target file not found: $Target"
}

$refData = Get-Content -LiteralPath $Reference -Raw -Encoding UTF8 | ConvertFrom-Json
$tgtData = Get-Content -LiteralPath $Target -Raw -Encoding UTF8 | ConvertFrom-Json

if ($refData -isnot [array]) { $refData = @($refData) }
if ($tgtData -isnot [array]) { $tgtData = @($tgtData) }

$fields = @('size', 'us_size', 'type', 'waist', 'hip', 'inseam', 'thigh', 'ankle')
$fieldNames = @{
    'size'    = '亚洲码'
    'us_size' = '美码'
    'type'    = '号型'
    'waist'   = '腰围'
    'hip'     = '臀围'
    'inseam'  = '内长'
    'thigh'   = '大腿围'
    'ankle'   = '脚口围'
}

$findings = [System.Collections.Generic.List[object]]::new()
$refSizes = $refData | ForEach-Object { $_.size } | Sort-Object
$tgtSizes = $tgtData | ForEach-Object { $_.size } | Sort-Object

$missingInTarget = Compare-Object $refSizes $tgtSizes |
    Where-Object SideIndicator -eq '<=' |
    ForEach-Object { $_.InputObject }

$extraInTarget = Compare-Object $refSizes $tgtSizes |
    Where-Object SideIndicator -eq '=>' |
    ForEach-Object { $_.InputObject }

if ($missingInTarget) {
    $findings.Add([pscustomobject]@{
        Status = 'MISSING'; Size = ($missingInTarget -join ', '); Field = '-'; Reference = '-'; Target = '-'
        Message = "目标尺码表缺少以下尺码: $($missingInTarget -join ', ')"
    })
}

if ($extraInTarget) {
    $findings.Add([pscustomobject]@{
        Status = 'NO-SOURCE'; Size = ($extraInTarget -join ', '); Field = '-'; Reference = '-'; Target = '-'
        Message = "目标尺码表包含知识库未记录的尺码: $($extraInTarget -join ', ')"
    })
}

foreach ($refRow in $refData) {
    $tgtRow = $tgtData | Where-Object { $_.size -eq $refRow.size } | Select-Object -First 1
    if (-not $tgtRow) { continue }

    foreach ($field in $fields) {
        $refVal = $refRow.$field
        $tgtVal = $tgtRow.$field

        if ($null -eq $tgtVal) {
            $findings.Add([pscustomobject]@{
                Status = 'MISSING'; Size = $refRow.size; Field = $fieldNames[$field]
                Reference = "$refVal"; Target = '(缺失)'
                Message = "$($refRow.size) 码的 $($fieldNames[$field]) 在目标表中缺失"
            })
            continue
        }

        if ("$refVal" -ne "$tgtVal") {
            $findings.Add([pscustomobject]@{
                Status = 'FAIL'; Size = $refRow.size; Field = $fieldNames[$field]
                Reference = "$refVal"; Target = "$tgtVal"
                Message = "$($refRow.size) 码 $($fieldNames[$field]): 知识库=$refVal, 目标=$tgtVal"
            })
        }
    }
}

$passCount = 0
foreach ($refRow in $refData) {
    $tgtRow = $tgtData | Where-Object { $_.size -eq $refRow.size } | Select-Object -First 1
    if ($tgtRow) {
        $allMatch = $true
        foreach ($field in $fields) {
            if ("$($tgtRow.$field)" -ne "$($refRow.$field)") { $allMatch = $false; break }
        }
        if ($allMatch) { $passCount++ }
    }
}

$failCount = @($findings | Where-Object Status -eq 'FAIL').Count
$missCount = @($findings | Where-Object Status -eq 'MISSING').Count
$noSrcCount = @($findings | Where-Object Status -eq 'NO-SOURCE').Count

Write-Output '尺码表比对结果摘要:'
Write-Output "  通过尺码数: $passCount / $($refData.Count)"
Write-Output "  不一致项: $failCount"
Write-Output "  缺失项: $missCount"
Write-Output "  无依据项: $noSrcCount"
Write-Output ''

if ($findings.Count -gt 0) {
    Write-Output '详细差异:'
    $findings | ForEach-Object { Write-Output "  [$($_.Status)] $($_.Message)" }
} else {
    Write-Output '所有尺码参数完全一致。'
}

if ($failCount -gt 0 -or $missCount -gt 0 -or $noSrcCount -gt 0) { exit 1 }
exit 0
