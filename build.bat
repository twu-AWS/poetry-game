@echo off
REM Windows 打包脚本

echo 🚀 开始打包诗词大闯关游戏 (Windows)...

REM 确保数据库存在
if not exist "poetry_game.db" (
    echo ⚠️  数据库文件不存在，正在创建...
    uv run init_poetry_db.py
)

REM 打包
uv run pyinstaller ^
    --name=诗词大闯关 ^
    --windowed ^
    --onefile ^
    --add-data=poetry_game.db;. ^
    poetry_game.py

echo.
echo ✅ 打包完成!
echo 📂 可执行文件位置: dist\诗词大闯关.exe
echo    双击运行即可!

pause
