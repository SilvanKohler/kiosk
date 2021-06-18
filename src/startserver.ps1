Stop-Process -Name Python
Start-Process -FilePath "C:\Windows\System32\cmd.exe" -ArgumentList "/C py server.py"