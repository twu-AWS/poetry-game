#!/bin/bash
# macOS/Linux 打包脚本

echo "🚀 开始打包诗词大闯关游戏 (macOS/Linux)..."

# 确保数据库存在
if [ ! -f "poetry_game.db" ]; then
    echo "⚠️  数据库文件不存在，正在创建..."
    uv run init_poetry_db.py
fi

# 打包
uv run pyinstaller \
    --name="诗词大闯关" \
    --windowed \
    --onefile \
    --add-data="poetry_game.db:." \
    --add-data="bg.png:." \
    poetry_game.py

echo ""
echo "✅ 打包完成!"
echo "📂 可执行文件位置:"

if [[ "$OSTYPE" == "darwin"* ]]; then
    echo "   dist/诗词大闯关.app"
    echo "   双击运行即可!"
else
    echo "   dist/诗词大闯关"
    echo "   运行: ./dist/诗词大闯关"
fi
