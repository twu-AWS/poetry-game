# 🏯 诗词大闯关游戏

一个适合四年级学生的Python诗词文言文填空游戏，包含100道题目（60首古诗 + 40篇文言文名篇）。

## 📚 题库内容

### 古诗部分 (60首)
- 经典唐诗：李白、杜甫、王维等
- 宋词选段：范成大、杨万里等
- 汉乐府、北朝民歌等

### 文言文部分 (40篇)
- 《陋室铭》刘禹锡
- 《爱莲说》周敦颐
- 《岳阳楼记》范仲淹
- 《桃花源记》陶渊明
- 《三峡》郦道元
- 《马说》韩愈

## 🎮 游戏玩法

1. 游戏开始时选择挑战题目数量（1-100题）
2. 每题显示一句古诗或文言文，挖掉一个关键词
3. 从四个选项中选择正确答案
4. 答对得10分，小人前进一格
5. 答错不扣分，但小人不动，可以继续尝试
6. 闯过所有关卡即为胜利！

## 🚀 使用方法

### 1. 创建虚拟环境

```bash
python3 -m venv venv
```

### 2. 安装依赖

```bash
./venv/bin/pip install duckdb
```

### 3. 初始化数据库

```bash
./venv/bin/python init_poetry_db.py
```

运行后会创建 `poetry_game.db` 数据库文件，包含100道题目。

### 4. 启动游戏

```bash
./venv/bin/python poetry_game.py
```

## 📦 打包为可执行文件

打包后的应用可以在没有 Python 环境的电脑上直接运行。

### 方式1：使用 GitHub Actions 自动打包（推荐）

**优点：** 一次配置，自动在 Windows 和 macOS 上打包，无需本地环境

**步骤：**

1. 将代码推送到 GitHub
2. 创建版本标签触发打包：
   ```bash
   git tag v1.0.0
   git push origin v1.0.0
   ```
3. 或在 GitHub Actions 页面手动触发 "Build Executables" 工作流
4. 等待 5-10 分钟后，在 Actions 页面下载打包好的文件：
   - `poetry-game-windows.zip` - Windows 版本
   - `poetry-game-macos.zip` - macOS 版本

**注意：** GitHub Actions 对公开仓库完全免费，私有仓库每月有 2000 分钟免费额度。

### 方式2：本地打包

**注意：** PyInstaller 不支持交叉编译，必须在目标平台上打包。

#### macOS

```bash
# 推荐方式 (onedir 模式，更稳定)
./build_mac.sh

# 或使用通用脚本
./build.sh
```

打包完成后：
- 可执行文件: `dist/诗词大闯关.app`
- 双击运行即可
- 可以拖到应用程序文件夹

#### Windows

```cmd
# 使用批处理脚本
build.bat

# 或使用 Python 脚本
uv run build.py
```

打包完成后：
- 可执行文件: `dist\诗词大闯关.exe`
- 双击运行即可
- 可以发送给其他 Windows 用户

#### Linux

```bash
./build.sh
```

打包完成后：
- 可执行文件: `dist/诗词大闯关`
- 运行: `./dist/诗词大闯关`

### 清理打包文件

```bash
# 所有平台
uv run build.py --clean
```

### 注意事项

- 首次打包需要下载依赖，可能需要几分钟
- 打包后的文件较大（约 30-50MB），因为包含了 Python 运行时
- macOS 用户首次运行可能需要在"系统偏好设置 > 安全性与隐私"中允许运行
- Windows 用户可能需要允许防火墙访问

## 📦 文件说明

- `poetry_game.py` - 游戏主程序
- `init_poetry_db.py` - 数据库初始化脚本
- `poetry_game.db` - 题库数据库（运行初始化脚本后生成）
- `README.md` - 说明文档

## 🛠️ 技术栈

- Python 3.x
- tkinter (GUI界面)
- DuckDB (本地数据库)

## 🎯 学习目标

- 巩固古诗词记忆
- 学习经典文言文名篇
- 培养语文素养
- 寓教于乐

## 📝 注意事项

- 首次运行前必须先执行 `init_poetry_db.py` 初始化数据库
- 游戏窗口大小：600x500像素
- 支持重新开始功能
- 题目每次随机抽取，不会重复

祝你玩得开心！📖✨
