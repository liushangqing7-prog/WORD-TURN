@echo off
chcp 65001 >nul
setlocal

title Word Turn Launcher
cd /d %~dp0

where python >nul 2>nul
if errorlevel 1 (
  echo [ERROR] 未检测到 Python，请先安装 Python 3.10+。
  pause
  exit /b 1
)

echo 正在启动 Word Turn...
python word_turn_launcher.py

if errorlevel 1 (
  echo [ERROR] 启动异常，请查看上方日志。
  pause
  exit /b 1
)

endlocal
