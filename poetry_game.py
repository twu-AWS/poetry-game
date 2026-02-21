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
        self.window.configure(bg="#FFF8DC")  # 米黄色背景
        
        # 游戏状态
        self.score = 0
        self.current_round = 0
        self.total_rounds = 8  # 总共8关
        self.questions = []  # 本局题目
        self.correct_count = 0  # 答对题数
        self.wrong_count = 0  # 答错题数
        
        # 创建界面
        self.create_widgets()
        
        # 开始新游戏
        self.start_new_game()
    
    def create_widgets(self):
        """创建游戏界面组件"""
        
        # ===== 顶部: 标题和分数 =====
        top_frame = tk.Frame(self.window, bg="#FFF8DC")
        top_frame.pack(fill="x", padx=20, pady=10)
        
        self.title_label = tk.Label(
            top_frame,
            text="🏯 诗词大闯关 🏯",
            font=("Microsoft YaHei", 24, "bold"),
            bg="#FFF8DC",
            fg="#8B4513"
        )
        self.title_label.pack()
        
        self.score_label = tk.Label(
            top_frame,
            text="得分: 0",
            font=("Microsoft YaHei", 16),
            bg="#FFF8DC",
            fg="#2E8B57"
        )
        self.score_label.pack()
        
        # ===== 进度条: 小人闯关 =====
        progress_frame = tk.Frame(self.window, bg="#FFF8DC")
        progress_frame.pack(fill="x", padx=20, pady=10)
        
        self.progress_canvas = tk.Canvas(
            progress_frame,
            width=560,
            height=60,
            bg="#90EE90",
            highlightthickness=2,
            highlightbackground="#228B22"
        )
        self.progress_canvas.pack()
        
        # 画关卡节点
        self.draw_progress()
        
        # ===== 中间: 诗词题目 =====
        question_frame = tk.Frame(self.window, bg="#FFF8DC")
        question_frame.pack(fill="x", padx=20, pady=10)
        
        self.poem_title_label = tk.Label(
            question_frame,
            text="",
            font=("Microsoft YaHei", 12),
            bg="#FFF8DC",
            fg="#666666"
        )
        self.poem_title_label.pack()
        
        self.question_label = tk.Label(
            question_frame,
            text="",
            font=("KaiTi", 22),
            bg="#FFF8DC",
            fg="#333333",
            wraplength=500
        )
        self.question_label.pack(pady=10)
        
        # ===== 选项按钮 =====
        options_frame = tk.Frame(self.window, bg="#FFF8DC")
        options_frame.pack(fill="x", padx=40, pady=10)
        
        self.option_buttons = []
        for i in range(4):
            btn = tk.Button(
                options_frame,
                text="",
                font=("Microsoft YaHei", 14),
                width=12,
                height=2,
                bg="#FFE4B5",
                activebackground="#FFD700",
                cursor="hand2",
                command=lambda idx=i: self.check_answer(idx)
            )
            btn.grid(row=i//2, column=i%2, padx=10, pady=5)
            self.option_buttons.append(btn)
        
        # ===== 底部: 提示信息 =====
        self.hint_label = tk.Label(
            self.window,
            text="选择正确的词语填入空格中吧!",
            font=("Microsoft YaHei", 12),
            bg="#FFF8DC",
            fg="#4169E1"
        )
        self.hint_label.pack(pady=10)
        
        # ===== 重新开始按钮 =====
        self.restart_btn = tk.Button(
            self.window,
            text="🔄 重新开始",
            font=("Microsoft YaHei", 12),
            bg="#87CEEB",
            activebackground="#00BFFF",
            cursor="hand2",
            command=self.start_new_game
        )
        self.restart_btn.pack(pady=10)
    
    def draw_progress(self):
        """画进度条和小人"""
        self.progress_canvas.delete("all")
        
        # 画路径
        self.progress_canvas.create_line(
            30, 30, 530, 30,
            width=4,
            fill="#228B22"
        )
        
        # 画关卡节点 (圆圈) - 只画关卡数量的节点
        step = 500 / (self.total_rounds - 1) if self.total_rounds > 1 else 0
        for i in range(self.total_rounds):
            x = 30 + int(i * step)
            color = "#FFD700" if i < self.current_round else "#FFFFFF"
            self.progress_canvas.create_oval(
                x-10, 20, x+10, 40,
                fill=color,
                outline="#228B22",
                width=2
            )
            if i < self.total_rounds - 1:
                # 普通关卡显示数字
                self.progress_canvas.create_text(
                    x, 50,
                    text=str(i+1),
                    font=("Arial", 10)
                )
            else:
                # 最后一关显示奖杯
                self.progress_canvas.create_text(
                    x, 50,
                    text="🏆",
                    font=("Arial", 12)
                )
        
        # 画小人 (在当前位置)
        if self.total_rounds > 1:
            x = 30 + int(self.current_round * step)
        else:
            x = 30
        self.progress_canvas.create_text(
            x, 5,
            text="🧒",
            font=("Arial", 16)
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
        
        self.score_label.config(text="得分: 0")
        self.hint_label.config(text="选择正确的词语填入空格中吧!", fg="#4169E1")
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
        self.poem_title_label.config(text=f"第 {self.current_round + 1} 关 - {type_label} - {q['title']}")
        self.question_label.config(text=q["question"])
        
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
            self.score_label.config(text=f"得分: {self.score}")
            self.option_buttons[idx].config(bg="#90EE90")
            self.hint_label.config(text="✨ 太棒了!答对了! ✨", fg="#228B22")
        else:
            # 答错了 - 不扣分，但显示正确答案
            self.wrong_count += 1
            self.option_buttons[idx].config(bg="#FFB6C1")

            # 显示正确答案
            for i, opt in enumerate(self.current_options):
                if opt == q["answer"]:
                    self.option_buttons[i].config(bg="#90EE90")

            self.hint_label.config(text=f"❌ 答错了!正确答案是: {q['answer']}", fg="#DC143C")

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

        self.hint_label.config(text="🎊 游戏结束!点击重新开始再玩一次 🎊", fg="#FF6347")
    
    def run(self):
        """运行游戏"""
        self.window.mainloop()


# ========== 程序入口 ==========
if __name__ == "__main__":
    game = PoetryGame()
    game.run()
