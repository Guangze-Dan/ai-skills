@echo off
rem 一键接入：把本仓库 skills junction 到各 AI agent 目录
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0install.ps1"
pause
