@echo off
chcp 65001 >nul
:: ============================================================
:: Zero Agent — 一键启动 / One-click Launcher
:: 不给架构预设。给循环、记忆、一个动作——让 LLM 自己长成 Agent。
:: No architecture preset. Loop, memory, one action — let the LLM grow.
:: ============================================================

:: 检查 .env / Check .env
if not exist ".env" (
    echo [错误/Error] .env 未找到 / not found
    echo 请复制 .env.example → .env，填入 API key
    echo Copy .env.example → .env, fill in your API key
    pause
    exit /b 1
)

:: 检查依赖 / Check dependencies
python -c "import openai, dotenv" 2>nul
if errorlevel 1 (
    echo [安装/Install] 缺少依赖，正在安装... / installing dependencies...
    pip install openai python-dotenv
    if errorlevel 1 (
        echo [错误/Error] 安装失败 / install failed
        pause
        exit /b 1
    )
)

:: 启动 / Launch
python main.py
pause
