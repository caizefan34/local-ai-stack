# 本地 Reranker 服务自动启动
# 启动命令：
Start-Process -WindowStyle Hidden -FilePath "python" -ArgumentList "/home/user\local-model-lab\reranker\server.py"

Write-Host "Reranker service started on port 18888"
