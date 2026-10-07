@echo off
rem No admin needed. Registers Ubuntu-24.04 in WSL (web download, no Store),
rem installs the lightpanda binary from D:\AgentSkills\sources\lightpanda into
rem it, and self-tests the CDP endpoint from Windows. Idempotent.
setlocal
set "LOG=D:\AgentSkills\logs\setup-distro.log"
set "DISTRO=Ubuntu-24.04"
set "BIN=D:\AgentSkills\sources\lightpanda\lightpanda-1.0.0-x86_64-linux"

if not exist "D:\AgentSkills\logs" mkdir "D:\AgentSkills\logs"
> "%LOG%" echo === lightpanda distro setup %DATE% %TIME% ===

wsl --status >nul 2>&1
if errorlevel 1 (
    echo WSL-MISSING: run admin-setup-wsl.cmd elevated first >> "%LOG%"
    echo WSL is not installed yet - run scripts\admin-setup-wsl.cmd elevated first.
    exit /b 1
)
wsl --version >> "%LOG%" 2>&1

wsl -d %DISTRO% --exec true >nul 2>&1
if errorlevel 1 (
    echo registering %DISTRO% via web download ...>> "%LOG%"
    wsl --install %DISTRO% --web-download --no-launch >> "%LOG%" 2>&1
    echo INSTALL-EXIT=%ERRORLEVEL%>> "%LOG%"
)

wsl -d %DISTRO% -u root --exec bash -c "echo DISTRO-OK" >> "%LOG%" 2>&1
if errorlevel 1 (
    echo DISTRO-START-FAILED >> "%LOG%"
    echo Could not run a command in %DISTRO% - check the log.
    exit /b 1
)

wsl -d %DISTRO% -u root --exec bash -c "mkdir -p /usr/local/lightpanda && cp /mnt/d/AgentSkills/sources/lightpanda/lightpanda-1.0.0-x86_64-linux /usr/local/lightpanda/lightpanda && chmod +x /usr/local/lightpanda/lightpanda && /usr/local/lightpanda/lightpanda --version || /usr/local/lightpanda/lightpanda version" >> "%LOG%" 2>&1

wsl -d %DISTRO% -u root --exec bash -c "ldd /usr/local/lightpanda/lightpanda 2>/dev/null | grep 'not found' | sort -u" > "%TEMP%\lp-missing-libs.txt" 2>&1
for /f "usebackq delims=" %%L in ("%TEMP%\lp-missing-libs.txt") do (
    echo missing lib: %%L - attempting apt install >> "%LOG%"
    wsl -d %DISTRO% -u root --exec bash -c "apt-get update -qq && apt-get install -y -qq libxml2 libexpat1" >> "%LOG%" 2>&1
    goto :libsdone
)
:libsdone

call "%~dp0lightpanda-start.cmd"
if errorlevel 1 (
    echo CDP-SELFTEST-FAILED >> "%LOG%"
    echo Started but CDP not reachable - check /var/log/lightpanda.log in the distro.
    exit /b 1
)
echo SETUP-OK >> "%LOG%"
echo Lightpanda installed and CDP verified on http://127.0.0.1:9222
endlocal
