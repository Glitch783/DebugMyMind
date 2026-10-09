Write-Host "Starting FastAPI backend on port 8000..." -ForegroundColor Cyan
$backendProcess = Start-Process python -ArgumentList "-m uvicorn app.main:app --host 0.0.0.0 --port 8000" -PassThru -NoNewWindow

# Give the backend a few seconds to start up
Start-Sleep -Seconds 3

Write-Host "Starting Streamlit frontend on port 8501..." -ForegroundColor Cyan
Write-Host "App running at http://localhost:8501" -ForegroundColor Green
python -m streamlit run frontend/home.py --server.port 8501

Write-Host "Shutting down backend process (PID $($backendProcess.Id))..." -ForegroundColor Yellow
Stop-Process -Id $backendProcess.Id -Force
