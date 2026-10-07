@echo off
rem Stop the lightpanda CDP server and shut the WSL VM down.
setlocal
set "DISTRO=Ubuntu-24.04"
wsl -d %DISTRO% -u root --exec bash -c "pkill -f 'lightpanda serve' || true" >nul 2>&1
wsl --terminate %DISTRO% >nul 2>&1
echo lightpanda stopped.
endlocal
