@echo off
chcp 936 >nul

set "ZEXE=D:\Zcode\apps\ZCode\ZCode.exe"
if exist "%ZEXE%" goto launch

rem Fallbacks, in case ZCode is moved or reinstalled elsewhere.
for %%P in (
    "%LOCALAPPDATA%\Programs\ZCode\ZCode.exe"
    "C:\Program Files\ZCode\ZCode.exe"
    "D:\ZCode\ZCode.exe"
) do (
    if exist %%P set "ZEXE=%%~P"
)
if not exist "%ZEXE%" goto missing

:launch
start "" "%ZEXE%"
exit /b 0

:missing
echo [ERROR] ZCode.exe not found. Looked in:
echo   D:\Zcode\apps\ZCode\ZCode.exe
echo   %LOCALAPPDATA%\Programs\ZCode\ZCode.exe
echo   C:\Program Files\ZCode\ZCode.exe
echo   D:\ZCode\ZCode.exe
echo Edit this file and set ZEXE to the correct path.
pause
exit /b 1
