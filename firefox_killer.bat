@echo off
:: Chiude Firefox in modo forzato (/F) e tutti i processi correlati (/T)
taskkill /F /IM firefox.exe /T

echo.
echo Firefox e stato arrestato. 
echo La finestra si chiudera automaticamente tra 5 secondi...

:: Attende 5 secondi (il numero dopo -n indica i secondi + 1)
ping 127.0.0.1 -n 6 > nul

exit