Write-Host "Starting BGE Reranker Service..." -ForegroundColor Green
pip install -r requirements.txt -q
python server.py
