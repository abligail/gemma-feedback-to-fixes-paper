param(
    [string]$Compiler = (Join-Path $env:LOCALAPPDATA 'GEMMA-paper-tools/tectonic-0.17.0/tectonic.exe'),
    [long]$SourceDateEpoch = 1794441600
)

$ErrorActionPreference = 'Stop'
$taskPaper = Split-Path -Parent $PSScriptRoot
if (-not (Test-Path -LiteralPath $Compiler -PathType Leaf)) {
    $taskCompilerCommand = Get-Command -Name $Compiler -CommandType Application -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($taskCompilerCommand) { $Compiler = $taskCompilerCommand.Source }
}
if (-not (Test-Path -LiteralPath $Compiler -PathType Leaf)) {
    $fallback = Join-Path $env:LOCALAPPDATA 'Packages/OpenAI.Codex_2p2nqsd0c76g0/LocalCache/Local/GEMMA-paper-tools/tectonic-0.17.0/tectonic.exe'
    if (Test-Path -LiteralPath $fallback -PathType Leaf) {
        $Compiler = $fallback
    } else {
        throw "Tectonic is missing. Pass -Compiler with an installed tectonic.exe path; see rendering.md."
    }
}
Push-Location $taskPaper
$taskPreviousEpoch = [Environment]::GetEnvironmentVariable('SOURCE_DATE_EPOCH')
try {
    # Freeze the PDF timestamp so a clean clone can reproduce the release bytes.
    $env:SOURCE_DATE_EPOCH = [string]$SourceDateEpoch
    New-Item -ItemType Directory -Path build -Force | Out-Null
    & $Compiler --keep-logs --outdir build main.tex
    if ($LASTEXITCODE -ne 0) { throw "Tectonic failed with exit code $LASTEXITCODE." }
    Write-Output (Join-Path $taskPaper 'build/main.pdf')
} finally {
    [Environment]::SetEnvironmentVariable('SOURCE_DATE_EPOCH', $taskPreviousEpoch)
    Pop-Location
}
