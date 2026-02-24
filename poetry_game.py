"""
诗词大闯关 - 四年级编程作业
用 Python tkinter 开发的诗词填空游戏

玩法:
- 显示一句古诗或文言文,挖掉一个词
- 从四个选项中选择正确答案
- 答对得10分,小人前进
- 答错不扣分,但小人不动
- 闯过所有关卡即为胜利!
"""

import tkinter as tk
from tkinter import messagebox
import random
import duckdb
import sys
import os


def get_resource_path(relative_path):
    """获取资源文件的绝对路径（支持打包后的应用）"""
    try:
        # PyInstaller 创建临时文件夹，路径存储在 _MEIPASS 中
        base_path = sys._MEIPASS
    except Exception:
        # 开发环境中使用当前目录
        base_path = os.path.abspath(".")
    
    return os.path.join(base_path, relative_path)

# ========== 数据库连接 ==========
def load_questions_from_db(num_questions):
    """从数据库随机抽取题目"""
    try:
        db_path = get_resource_path('poetry_game.db')
        conn = duckdb.connect(db_path, read_only=True)
        
        # 随机抽取指定数量的题目
        query = f"""
            SELECT full_text, question, answer, options, title, type
            FROM poems
            ORDER BY RANDOM()
            LIMIT {num_questions}
        """
        
        results = conn.execute(query).fetchall()
        conn.close()
        
        # 转换为游戏需要的格式
        questions = []
        for row in results:
            full, question, answer, options_str, title, ptype = row
            options = options_str.split('|')
            
            questions.append({
                "full": full,
                "question": question,
                "answer": answer,
                "options": options,
                "title": title,
                "type": ptype
            })
        
        return questions
    except Exception as e:
        messagebox.showerror("数据库错误", f"无法加载题目:\n{e}\n\n请先运行 init_poetry_db.py 初始化数据库!")
        return []


def get_total_questions_count():
    """获取数据库中的总题目数"""
    try:
        db_path = get_resource_path('poetry_game.db')
        conn = duckdb.connect(db_path, read_only=True)
        count = conn.execute("SELECT COUNT(*) FROM poems").fetchone()[0]
        conn.close()
        return count
    except:
        return 12  # 默认值


class PoetryGame:
    """诗词大闯关游戏主类"""
    
    def __init__(self):
        # 创建主窗口
        self.window = tk.Tk()
        self.window.title("🏯 诗词大闯关 🏯")
        self.window.geometry("600x500")
        
        # 游戏状态
        self.score = 0
        self.current_round = 0
        self.total_rounds = 8  # 总共8关
        self.questions = []  # 本局题目
        self.correct_count = 0  # 答对题数
        self.wrong_count = 0  # 答错题数
        
        # 创建Canvas作为主容器
        self.canvas = tk.Canvas(self.window, width=600, height=500, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        
        # 加载并设置背景图片
        self.load_background()
        
        # 创建界面
        self.create_widgets()
        
        # 开始新游戏
        self.start_new_game()
    
    def load_background(self):
        """加载背景图片"""
        try:
            bg_image_path = get_resource_path('bg.png')
            # 使用tkinter的PhotoImage直接加载PNG
            self.bg_photo = tk.PhotoImage(file=bg_image_path)
            
            # 在Canvas上绘制背景
            self.canvas.create_image(0, 0, image=self.bg_photo, anchor="nw", tags="bg")
            print("背景图片加载成功")
        except Exception as e:
            print(f"无法加载背景图片: {e}")
            self.canvas.configure(bg="#FFF8DC")
            import traceback
            traceback.print_exc()
    
    def create_widgets(self):
        """创建游戏界面组件 - 使用Canvas绘制"""
        
        # ===== 顶部: 标题和分数 (使用Canvas文本) =====
        self.title_text = self.canvas.create_text(
            300, 30,
            text="🏯 诗词大闯关 🏯",
            font=("Microsoft YaHei", 24, "bold"),
            fill="#8B4513",
            tags="ui"
        )
        
        self.score_text = self.canvas.create_text(
            300, 65,
            text="得分: 0",
            font=("Microsoft YaHei", 16),
            fill="#2E8B57",
            tags="ui"
        )
        
        # ===== 进度条区域 =====
        self.progress_y = 110
        
        # ===== 中间: 诗词题目 =====
        self.poem_title_text = self.canvas.create_text(
            300, 180,
            text="",
            font=("Microsoft YaHei", 12),
            fill="#666666",
            tags="ui"
        )
        
        self.question_text = self.canvas.create_text(
            300, 220,
            text="",
            font=("KaiTi", 22),
            fill="#333333",
            width=500,
            tags="ui"
        )
        
        # ===== 选项按钮 (使用真实按钮，但放在Canvas上) =====
        self.option_buttons = []
        button_y_start = 280
        for i in range(4):
            row = i // 2
            col = i % 2
            x = 150 + col * 200
            y = button_y_start + row * 60
            
            btn = tk.Button(
                self.canvas,
                text="",
                font=("Microsoft YaHei", 14),
                width=12,
                height=2,
                bg="#FFE4B5",
                activebackground="#FFD700",
                cursor="hand2",
                command=lambda idx=i: self.check_answer(idx)
            )
            self.canvas.create_window(x, y, window=btn, tags="ui")
            self.option_buttons.append(btn)
        
        # ===== 底部: 提示信息 =====
        self.hint_text = self.canvas.create_text(
            300, 420,
            text="选择正确的词语填入空格中吧!",
            font=("Microsoft YaHei", 12),
            fill="#4169E1",
            tags="ui"
        )
        
        # ===== 重新开始按钮 =====
        self.restart_btn = tk.Button(
            self.canvas,
            text="🔄 重新开始",
            font=("Microsoft YaHei", 12),
            bg="#87CEEB",
            activebackground="#00BFFF",
            cursor="hand2",
            command=self.start_new_game
        )
        self.canvas.create_window(300, 460, window=self.restart_btn, tags="ui")
    
    def draw_progress(self):
        """画进度条和小人 - 直接在主Canvas上绘制"""
        # 删除旧的进度条元素
        self.canvas.delete("progress")
        
        y = self.progress_y
        
        # 画路径
        self.canvas.create_line(
            50, y, 550, y,
            width=4,
            fill="#228B22",
            tags="progress"
        )
        
        # 画关卡节点 (圆圈)
        step = 500 / (self.total_rounds - 1) if self.total_rounds > 1 else 0
        for i in range(self.total_rounds):
            x = 50 + int(i * step)
            color = "#FFD700" if i < self.current_round else "#FFFFFF"
            self.canvas.create_oval(
                x-10, y-10, x+10, y+10,
                fill=color,
                outline="#228B22",
                width=2,
                tags="progress"
            )
            if i < self.total_rounds - 1:
                # 普通关卡显示数字
                self.canvas.create_text(
                    x, y+20,
                    text=str(i+1),
                    font=("Arial", 10),
                    tags="progress"
                )
            else:
                # 最后一关显示奖杯
                self.canvas.create_text(
                    x, y+20,
                    text="🏆",
                    font=("Arial", 12),
                    tags="progress"
                )
        
        # 画小人 (在当前位置)
        if self.total_rounds > 1:
            x = 50 + int(self.current_round * step)
        else:
            x = 50
        self.canvas.create_text(
            x, y-25,
            text="🧒",
            font=("Arial", 16),
            tags="progress"
        )
    
    def start_new_game(self):
        """开始新游戏"""
        # 弹窗让学生选择题目数量
        from tkinter import simpledialog
        
        total_in_db = get_total_questions_count()
        
        num_questions = simpledialog.askinteger(
            "选择关卡数",
            f"你想挑战几道题？\n(题库共有 {total_in_db} 道题，包含古诗和文言文)",
            minvalue=1,
            maxvalue=total_in_db,
            initialvalue=8
        )
        
        # 如果取消了，使用默认值
        if num_questions is None:
            num_questions = 8
        
        self.total_rounds = num_questions
        self.score = 0
        self.current_round = 0
        self.correct_count = 0
        self.wrong_count = 0
        
        # 从数据库加载题目
        self.questions = load_questions_from_db(self.total_rounds)
        
        if not self.questions:
            # 如果加载失败，退出
            self.window.destroy()
            return
        
        self.canvas.itemconfig(self.score_text, text="得分: 0")
        self.canvas.itemconfig(self.hint_text, text="选择正确的词语填入空格中吧!", fill="#4169E1")
        self.draw_progress()
        
        # 显示第一题
        self.show_question()
    
    def show_question(self):
        """显示当前题目"""
        if self.current_round >= self.total_rounds:
            self.game_over(True)
            return
        
        q = self.questions[self.current_round]
        
        # 显示题目类型标签
        type_label = "📜 古诗" if q.get("type") == "古诗" else "📖 文言文"
        self.canvas.itemconfig(
            self.poem_title_text,
            text=f"第 {self.current_round + 1} 关 - {type_label} - {q['title']}"
        )
        self.canvas.itemconfig(self.question_text, text=q["question"])
        
        # 打乱选项顺序
        options = q["options"].copy()
        random.shuffle(options)
        self.current_options = options
        
        for i, btn in enumerate(self.option_buttons):
            btn.config(
                text=options[i],
                bg="#FFE4B5",
                state="normal"
            )
    
    def check_answer(self, idx):
        """检查答案"""
        q = self.questions[self.current_round]
        selected = self.current_options[idx]

        # 禁用所有按钮，防止重复点击和重试
        for btn in self.option_buttons:
            btn.config(state="disabled")

        if selected == q["answer"]:
            # 答对了!
            self.score += 10
            self.correct_count += 1
            self.canvas.itemconfig(self.score_text, text=f"得分: {self.score}")
            self.option_buttons[idx].config(bg="#90EE90")
            self.canvas.itemconfig(self.hint_text, text="✨ 太棒了!答对了! ✨", fill="#228B22")
        else:
            # 答错了 - 不扣分，但显示正确答案
            self.wrong_count += 1
            self.option_buttons[idx].config(bg="#FFB6C1")

            # 显示正确答案
            for i, opt in enumerate(self.current_options):
                if opt == q["answer"]:
                    self.option_buttons[i].config(bg="#90EE90")

            self.canvas.itemconfig(self.hint_text, text=f"❌ 答错了!正确答案是: {q['answer']}", fill="#DC143C")

        # 前进到下一关
        self.current_round += 1
        self.draw_progress()

        # 检查是否通关
        if self.current_round >= self.total_rounds:
            self.window.after(2000, lambda: self.game_over(True))
        else:
            # 延迟显示下一题
            self.window.after(2000, self.show_question)
    
    def game_over(self, won):
        """游戏结束"""
        if won:
            # 计算正确率
            accuracy = (self.correct_count / self.total_rounds * 100) if self.total_rounds > 0 else 0

            # 根据得分给出评价
            if accuracy >= 90:
                comment = "完美!你是真正的诗词大师! 🌟"
            elif accuracy >= 80:
                comment = "非常棒!继续加油! 💪"
            elif accuracy >= 70:
                comment = "不错哦!再接再厉! 👍"
            elif accuracy >= 60:
                comment = "还可以,多多练习! 📚"
            else:
                comment = "加油!熟能生巧! 💪"

            msg = f"""🎉 游戏结束! 🎉

    📊 成绩统计:
    ━━━━━━━━━━━━━━━━
    总题数: {self.total_rounds} 题
    答对: {self.correct_count} 题 ✅
    答错: {self.wrong_count} 题 ❌
    正确率: {accuracy:.1f}%
    ━━━━━━━━━━━━━━━━
    总得分: {self.score} 分

    {comment}"""
            messagebox.showinfo("游戏结束", msg)

        self.canvas.itemconfig(self.hint_text, text="🎊 游戏结束!点击重新开始再玩一次 🎊", fill="#FF6347")
    
    def run(self):
        """运行游戏"""
        self.window.mainloop()


# ========== 程序入口 ==========
if __name__ == "__main__":
    game = PoetryGame()
    game.run()
