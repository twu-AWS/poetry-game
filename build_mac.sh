#!/bin/bash
# macOS 专用打包脚本 (使用 onedir 模式)

echo "🚀 开始打包诗词大闯关游戏 (macOS)..."

# 确保数据库存在
if [ ! -f "poetry_game.db" ]; then
    echo "⚠️  数据库文件不存在，正在创建..."
    uv run init_poetry_db.py
fi

# 打包 (使用 onedir 模式，更适合 macOS)
uv run pyinstaller \
    --name="诗词大闯关" \
    --windowed \
    --onedir \
    --add-data="poetry_game.db:." \
    --add-data="bg.png:." \
    poetry_game.py

echo ""
echo "✅ 打包完成!"
echo "📂 可执行文件位置: dist/诗词大闯关.app"
echo "   双击运行即可!"
echo ""
echo "💡 提示: 可以将整个 诗词大闯关.app 拖到应用程序文件夹"
