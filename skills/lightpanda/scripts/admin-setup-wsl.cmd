@echo off
rem Run ELEVATED (one UAC click). Enables the Windows features WSL needs and
rem installs the WSL 3.0.1 MSI. Never reboots by itself: read the log line
rem "reboot required" in D:\AgentSkills\logs\admin-setup-wsl.log afterwards.
setlocal
set "LOG=D:\AgentSkills\logs\admin-setup-wsl.log"
if not exist "D:\AgentSkills\logs" mkdir "D:\AgentSkills\logs"

> "%LOG%" echo === admin WSL setup %DATE% %TIME% ===

dism /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart >> "%LOG%" 2>&1
echo DISM-VMP-EXIT=%ERRORLEVEL%>> "%LOG%"

dism /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart >> "%LOG%" 2>&1
echo DISM-WSL-EXIT=%ERRORLEVEL%>> "%LOG%"

msiexec /i "D:\AgentSkills\sources\wsl\wsl.3.0.1.0.x64.msi" /qn /norestart /L* "%TEMP%\wsl-msi-install.log"
echo MSI-EXIT=%ERRORLEVEL%>> "%LOG%"

findstr /i /c:"restart" /c:"reboot" "%TEMP%\wsl-msi-install.log" >> "%LOG%" 2>nul
wsl --version >> "%LOG%" 2>&1
echo DONE>> "%LOG%"
endlocal
