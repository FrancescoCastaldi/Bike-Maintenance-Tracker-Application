param(
    [string]$Source = "bike_track.c",
    [string]$Output = "bike_track.exe",
    [switch]$Clean
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Test-Compiler {
    foreach ($candidate in @('gcc', 'clang')) {
        if (Get-Command $candidate -ErrorAction SilentlyContinue) {
            return $candidate
        }
    }
    return $null
}

if ($Clean -and (Test-Path $Output)) {
    Remove-Item $Output -Force
}

$compiler = Test-Compiler
if (-not $compiler) {
    Write-Error "Nessun compilatore C trovato. Installa Mingw-w64 (gcc) o LLVM (clang) e assicurati che sia nel PATH."
    exit 1
}

if (-not (Test-Path $Output) -or (Get-Item $Output).LastWriteTime -lt (Get-Item $Source).LastWriteTime) {
    Write-Host "Compilazione di $Source con $compiler..." -ForegroundColor Cyan
    & $compiler $Source -o $Output
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Compilazione fallita con codice $LASTEXITCODE."
        exit $LASTEXITCODE
    }
}

Write-Host "Avvio dell'applicazione..." -ForegroundColor Green
& .\$Output
exit $LASTEXITCODE
