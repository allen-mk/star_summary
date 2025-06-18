@echo off
REM 虚拟环境快速设置脚本 (Windows)

echo 🌟 GitHub Star Summary - 虚拟环境快速设置
echo ============================================================

REM 检查 Python 是否安装
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ 未找到 Python，请先安装 Python 3.8 或更高版本
    echo 💡 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

REM 显示 Python 版本
echo 🐍 检测到的 Python 版本:
python --version

REM 运行 Python 设置脚本
echo 🚀 开始设置虚拟环境...
python scripts\setup_env.py

echo.
echo 🎉 设置完成！请运行以下命令激活虚拟环境：
echo activate.bat
pause
