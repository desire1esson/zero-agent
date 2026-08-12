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
    echo.
    echo 获取 API key: https://platform.deepseek.com
    echo 然后复制 .env.example → .env，填入 key
    echo.
    echo Get API key: https://platform.deepseek.com
    echo Then copy .env.example → .env, fill in your key
    pause
    exit /b 1
)

:: 检查 API key 不是占位符 / Check key is not placeholder
findstr /C:"DEEPSEEK_API_KEY=***" .env >nul
if not errorlevel 1 (
    echo [错误/Error] API key 仍未填入 / still placeholder "***"
    echo.
    echo 获取 API key: https://platform.deepseek.com
    echo 编辑 .env，把 *** 换成真实 key
    echo.
    echo Get API key: https://platform.deepseek.com
    echo Edit .env, replace *** with your real key
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
