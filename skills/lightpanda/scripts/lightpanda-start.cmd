@echo off
rem Start the lightpanda CDP server detached inside WSL and wait until it
rem answers on http://127.0.0.1:9222. Exits 0 if already running or started.
setlocal
set "DISTRO=Ubuntu-24.04"
set "PORT=9222"

curl -s -o nul http://127.0.0.1:%PORT%/json/version
if not errorlevel 1 (
    echo lightpanda already running at http://127.0.0.1:%PORT%
    exit /b 0
)

wsl -d %DISTRO% -u root --exec bash -c "pgrep -f 'lightpanda serve' >/dev/null || setsid nohup /usr/local/lightpanda/lightpanda serve --port %PORT% >/var/log/lightpanda.log 2>&1 </dev/null & sleep 1" >nul 2>&1

set /a tries=0
:waitloop
curl -s -o nul http://127.0.0.1:%PORT%/json/version
if not errorlevel 1 goto :up
set /a tries+=1
if %tries% lss 15 (
    timeout /t 1 /nobreak >nul
    goto :waitloop
)

echo lightpanda did not come up on port %PORT% within 15s.
echo Check the log:  wsl -d %DISTRO% -u root -- cat /var/log/lightpanda.log
exit /b 1

:up
echo lightpanda CDP ready at http://127.0.0.1:%PORT%
endlocal
exit /b 0
