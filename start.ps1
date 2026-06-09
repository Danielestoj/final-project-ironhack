param([switch]$NoBrowser)

$Root = $PSScriptRoot

Write-Host "=== Iniciando Asistente D&D ===" -ForegroundColor Green

# 1. BACKEND
Write-Host "[1/3] Iniciando Backend (puerto 8000)..." -ForegroundColor Cyan
Start-Process -WindowStyle Normal -FilePath "powershell" -ArgumentList @(
    "-NoExit", "-Command",
    "cd '$Root\backend'; .\venv\Scripts\Activate; uvicorn main:app --reload --host 127.0.0.1 --port 8000"
)

Start-Sleep -Seconds 2

# 2. FRONTEND
Write-Host "[2/3] Iniciando Frontend (puerto 5173)..." -ForegroundColor Cyan
Start-Process -WindowStyle Normal -FilePath "powershell" -ArgumentList @(
    "-NoExit", "-Command",
    "cd '$Root\frontend'; npm run dev"
)

Start-Sleep -Seconds 1

# 3. N8N (Docker)
$dockerExe = "C:\Program Files\Docker\Docker\resources\bin\docker.exe"
Write-Host "[3/3] Iniciando n8n (puerto 5678)..." -ForegroundColor Cyan
Start-Process -WindowStyle Normal -FilePath "powershell" -ArgumentList @(
    "-NoExit", "-Command",
    "if (`$(& '$dockerExe' ps -a --filter name=^/n8n`$ --format '{{.Names}}')) { & '$dockerExe' start n8n } else { & '$dockerExe' run -d --name n8n -p 5678:5678 -v n8n_data:/home/node/.n8n n8nio/n8n }"
)

# Abrir Chrome con 3 pestañas
if (-not $NoBrowser) {
    Write-Host "Esperando a que los servicios arranquen (8s)..." -ForegroundColor Yellow
    Start-Sleep -Seconds 8
    $chromeCandidates = @(
        "C:\Program Files\Google\Chrome\Application\chrome.exe",
        "$env:LOCALAPPDATA\Google\Chrome\Application\chrome.exe",
        "C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
    )
    $chrome = $null
    foreach ($candidate in $chromeCandidates) {
        if (Test-Path $candidate) {
            $chrome = $candidate
            break
        }
    }
    if ($chrome) {
        Write-Host "Abriendo Chrome..." -ForegroundColor Green
        Start-Process $chrome -ArgumentList @(
            "http://localhost:5173",
            "http://localhost:8000/docs",
            "http://localhost:5678"
        )
    } else {
        Write-Host "Chrome no encontrado. Abre manualmente:" -ForegroundColor Yellow
        Write-Host "  http://localhost:5173"
        Write-Host "  http://localhost:8000/docs"
        Write-Host "  http://localhost:5678"
    }
}

Write-Host "=== Hecho. Cierra las ventanas de terminal para detener los servicios ===" -ForegroundColor Green
