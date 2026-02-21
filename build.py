#!/usr/bin/env python3
"""
打包脚本 - 将诗词游戏打包为可执行文件
支持 macOS 和 Windows
"""

import os
import sys
import subprocess
import shutil

def build_app():
    """打包应用"""
    
    print("🚀 开始打包诗词大闯关游戏...")
    
    # 确保数据库文件存在
    if not os.path.exists('poetry_game.db'):
        print("⚠️  数据库文件不存在，正在创建...")
        subprocess.run([sys.executable, 'init_poetry_db.py'], check=True)
    
    # PyInstaller 打包命令
    cmd = [
        'pyinstaller',
        '--name=诗词大闯关',
        '--windowed',  # 不显示控制台窗口
        '--onefile',   # 打包成单个文件
        '--add-data=poetry_game.db:.',  # 包含数据库文件
        '--icon=NONE',  # 可以后续添加图标
        'poetry_game.py'
    ]
    
    # Windows 和 macOS 的数据文件路径分隔符不同
    if sys.platform == 'win32':
        cmd[4] = '--add-data=poetry_game.db;.'
    
    print(f"📦 执行打包命令: {' '.join(cmd)}")
    
    try:
        subprocess.run(cmd, check=True)
        print("\n✅ 打包成功!")
        
        # 显示输出位置
        if sys.platform == 'darwin':
            print(f"\n📂 可执行文件位置: dist/诗词大闯关.app")
            print("   双击运行即可!")
        elif sys.platform == 'win32':
            print(f"\n📂 可执行文件位置: dist\\诗词大闯关.exe")
            print("   双击运行即可!")
        else:
            print(f"\n📂 可执行文件位置: dist/诗词大闯关")
            print("   运行: ./dist/诗词大闯关")
        
        print("\n💡 提示: 可以将 dist 目录中的文件分发给其他用户")
        
    except subprocess.CalledProcessError as e:
        print(f"\n❌ 打包失败: {e}")
        sys.exit(1)


def clean():
    """清理打包产生的临时文件"""
    print("🧹 清理临时文件...")
    
    dirs_to_remove = ['build', 'dist', '__pycache__']
    files_to_remove = ['诗词大闯关.spec']
    
    for d in dirs_to_remove:
        if os.path.exists(d):
            shutil.rmtree(d)
            print(f"   删除目录: {d}")
    
    for f in files_to_remove:
        if os.path.exists(f):
            os.remove(f)
            print(f"   删除文件: {f}")
    
    print("✅ 清理完成!")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='打包诗词大闯关游戏')
    parser.add_argument('--clean', action='store_true', help='清理打包产生的临时文件')
    
    args = parser.parse_args()
    
    if args.clean:
        clean()
    else:
        build_app()
