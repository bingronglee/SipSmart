import sqlite3
import tkinter as tk
from tkinter import ttk
from datetime import datetime, time
import threading
import time as time_module

class WaterReminderApp:
    def __init__(self):
        self.init_database()
        self.setup_ui()

    def init_database(self):
        # 连接到SQLite数据库（如果不存在则创建）
        self.conn = sqlite3.connect('water_reminder.db')
        self.cursor = self.conn.cursor()

        # 创建用户设置表
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_settings (
            id INTEGER PRIMARY KEY,
            daily_goal INTEGER DEFAULT 2000,
            reminder_enabled BOOLEAN DEFAULT 1,
            reminder_interval INTEGER DEFAULT 30,
            reminder_start TIME DEFAULT '08:00',
            reminder_end TIME DEFAULT '22:00'
        )
        ''')

        # 创建喝水记录表
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS water_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            amount INTEGER,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        ''')

        # 初始化用户设置（如果不存在）
        self.cursor.execute('INSERT OR IGNORE INTO user_settings (id) VALUES (1)')
        self.conn.commit()

    def setup_ui(self):
        self.root = tk.Tk()
        self.root.title('飲水提醒應用')
        self.root.geometry('800x600')

        # 创建标签页
        notebook = ttk.Notebook(self.root)
        notebook.pack(expand=True, fill='both', padx=10, pady=5)

        # 主页面
        home_frame = ttk.Frame(notebook)
        notebook.add(home_frame, text='今日飲水')
        self.setup_home_page(home_frame)

        # 设置页面
        settings_frame = ttk.Frame(notebook)
        notebook.add(settings_frame, text='設定')
        self.setup_settings_page(settings_frame)

        # 启动提醒线程
        self.reminder_thread = threading.Thread(target=self.reminder_loop, daemon=True)
        self.reminder_thread.start()

    def setup_home_page(self, parent):
        # 显示今日进度
        progress_frame = ttk.LabelFrame(parent, text='今日進度')
        progress_frame.pack(fill='x', padx=10, pady=5)

        self.progress_var = tk.StringVar(value='0%')
        progress_label = ttk.Label(progress_frame, textvariable=self.progress_var, font=('Helvetica', 24))
        progress_label.pack(pady=10)

        # 快速添加按钮
        buttons_frame = ttk.LabelFrame(parent, text='快速添加')
        buttons_frame.pack(fill='x', padx=10, pady=5)

        amounts = [30, 50, 100]
        for amount in amounts:
            btn = ttk.Button(buttons_frame, text=f'{amount}ml',
                           command=lambda a=amount: self.add_water_record(a))
            btn.pack(side='left', padx=5, pady=5)

        # 显示最近记录
        records_frame = ttk.LabelFrame(parent, text='最近記錄')
        records_frame.pack(fill='both', expand=True, padx=10, pady=5)

        self.records_tree = ttk.Treeview(records_frame, columns=('time', 'amount'), show='headings')
        self.records_tree.heading('time', text='時間')
        self.records_tree.heading('amount', text='數量 (ml)')
        self.records_tree.pack(fill='both', expand=True)

        self.update_home_page()

    def setup_settings_page(self, parent):
        # 每日目标设置
        goal_frame = ttk.LabelFrame(parent, text='每日目標')
        goal_frame.pack(fill='x', padx=10, pady=5)

        self.goal_var = tk.StringVar()
        goal_entry = ttk.Entry(goal_frame, textvariable=self.goal_var)
        goal_entry.pack(side='left', padx=5, pady=5)
        ttk.Label(goal_frame, text='ml').pack(side='left')

        # 提醒设置
        reminder_frame = ttk.LabelFrame(parent, text='提醒設定')
        reminder_frame.pack(fill='x', padx=10, pady=5)

        self.reminder_enabled = tk.BooleanVar()
        ttk.Checkbutton(reminder_frame, text='啟用提醒',
                       variable=self.reminder_enabled).pack(pady=5)

        interval_frame = ttk.Frame(reminder_frame)
        interval_frame.pack(fill='x', pady=5)
        ttk.Label(interval_frame, text='提醒間隔：').pack(side='left')
        self.interval_var = tk.StringVar()
        ttk.Entry(interval_frame, textvariable=self.interval_var,
                  width=10).pack(side='left')
        ttk.Label(interval_frame, text='分鐘').pack(side='left')

        # 保存按钮
        ttk.Button(parent, text='儲存設定',
                   command=self.save_settings).pack(pady=10)

        # 加载当前设置
        self.load_settings()

    def add_water_record(self, amount):
        self.cursor.execute('INSERT INTO water_records (amount) VALUES (?)', (amount,))
        self.conn.commit()
        self.update_home_page()

    def add_custom_amount(self):
        try:
            amount = int(self.custom_amount.get())
            if amount > 0:
                self.add_water_record(amount)
                self.custom_amount.delete(0, tk.END)
        except ValueError:
            pass

    def update_home_page(self):
        # 获取今日记录
        today = datetime.now().strftime('%Y-%m-%d')
        self.cursor.execute('''
        SELECT SUM(amount) FROM water_records
        WHERE date(timestamp) = date(?)
        ''', (today,))
        total = self.cursor.fetchone()[0] or 0

        # 获取目标
        self.cursor.execute('SELECT daily_goal FROM user_settings WHERE id = 1')
        goal = self.cursor.fetchone()[0]

        # 更新进度
        progress = min(100, int(total * 100 / goal))
        self.progress_var.set(f'{progress}% ({total}/{goal}ml)')

        # 更新记录列表
        for item in self.records_tree.get_children():
            self.records_tree.delete(item)

        self.cursor.execute('''
        SELECT timestamp, amount FROM water_records
        WHERE date(timestamp) = date(?)
        ORDER BY timestamp DESC
        ''', (today,))

        for record in self.cursor.fetchall():
            time_str = datetime.strptime(record[0], '%Y-%m-%d %H:%M:%S').strftime('%H:%M')
            self.records_tree.insert('', 'end', values=(time_str, f'{record[1]}ml'))

    def load_settings(self):
        self.cursor.execute('''
        SELECT daily_goal, reminder_enabled, reminder_interval
        FROM user_settings WHERE id = 1
        ''')
        settings = self.cursor.fetchone()
        if settings:
            self.goal_var.set(str(settings[0]))
            self.reminder_enabled.set(bool(settings[1]))
            self.interval_var.set(str(settings[2]))

    def save_settings(self):
        try:
            goal = int(self.goal_var.get())
            interval = int(self.interval_var.get())
            if goal > 0 and interval > 0:
                self.cursor.execute('''
                UPDATE user_settings
                SET daily_goal = ?, reminder_enabled = ?, reminder_interval = ?
                WHERE id = 1
                ''', (goal, self.reminder_enabled.get(), interval))
                self.conn.commit()
                self.update_home_page()
        except ValueError:
            pass

    def reminder_loop(self):
        while True:
            self.cursor.execute('''
            SELECT reminder_enabled, reminder_interval
            FROM user_settings WHERE id = 1
            ''')
            settings = self.cursor.fetchone()
            if settings and settings[0]:  # 如果启用了提醒
                # 检查是否需要提醒
                current_time = datetime.now().time()
                if time(8, 0) <= current_time <= time(22, 0):
                    self.show_reminder()
                time_module.sleep(settings[1] * 60)  # 等待设定的间隔时间
            else:
                time_module.sleep(60)  # 如果禁用了提醒，每分钟检查一次设置变化

    def show_reminder(self):
        reminder_window = tk.Toplevel(self.root)
        reminder_window.title('飲水提醒')
        reminder_window.geometry('300x150')

        ttk.Label(reminder_window, text='該喝水啦！',
                  font=('Helvetica', 16)).pack(pady=20)
        ttk.Button(reminder_window, text='好的',
                   command=reminder_window.destroy).pack()

    def run(self):
        self.root.mainloop()

if __name__ == '__main__':
    app = WaterReminderApp()
    app.run()
