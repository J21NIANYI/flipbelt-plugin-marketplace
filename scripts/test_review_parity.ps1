[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'
$repo = Split-Path -Parent $PSScriptRoot
$script = Join-Path $repo 'plugins\flipbelt-product-intelligence\skills\flipbelt-review-specialist\scripts\compare_size_chart.ps1'
$fixtureRoot = Join-Path $repo 'tests\review-parity'
$reference = Join-Path $fixtureRoot 'reference.json'

function Invoke-Case([string]$Name, [string]$TargetName, [int]$ExpectedExit, [string[]]$Required) {
    $target = Join-Path $fixtureRoot $TargetName
    $output = & pwsh -NoProfile -File $script -Reference $reference -Target $target 2>&1
    $exitCode = $LASTEXITCODE
    $text = $output -join "`n"
    if ($exitCode -ne $ExpectedExit) { throw "${Name}: expected exit $ExpectedExit, got $exitCode" }
    foreach ($item in $Required) {
        if (-not $text.Contains($item)) { throw "${Name}: missing expected behavior '$item'" }
    }
    [pscustomobject]@{ Case = $Name; ExitCode = $exitCode; RequiredBehavior = $true }
}

$results = @(
    Invoke-Case -Name 'pass-reordered' -TargetName 'target-pass-reordered.json' -ExpectedExit 0 -Required @('通过尺码数: 2 / 2','不一致项: 0','缺失项: 0','无依据项: 0','所有尺码参数完全一致。')
    Invoke-Case -Name 'differences' -TargetName 'target-differences.json' -ExpectedExit 1 -Required @('通过尺码数: 0 / 2','不一致项: 1','缺失项: 2','无依据项: 1','[MISSING]','[NO-SOURCE]','[FAIL]')
)

$results | Format-Table -AutoSize
Write-Output "PUBLIC REVIEW PARITY PASSED: cases=$($results.Count)"
