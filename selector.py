import tkinter as tk
import json
import os

CONFIG_FILE = "config.json"


class MinimapSelector:
    def __init__(self, root):
        self.root = root
        self.root.title("小地图校准器")

        # --- 窗口样式设置 ---
        self.root.overrideredirect(True)  # 去除系统窗口边框
        self.root.attributes("-topmost", True)  # 永远置顶
        self.root.attributes("-alpha", 0.5)  # 设置整体半透明(50%)，方便看透下方的游戏
        self.root.configure(bg='black')  # 背景纯黑

        # --- 初始化状态 ---
        self.size = 150
        self.x = 100
        self.y = 100

        # 从现有配置文件中读取上一次的位置
        self.load_initial_pos()

        # 设置初始位置和大小
        self.root.geometry(f"{self.size}x{self.size}+{self.x}+{self.y}")

        # --- 创建画布 ---
        self.canvas = tk.Canvas(root, bg='black', highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.draw_ui()

        # --- 绑定鼠标与键盘事件 ---
        self.canvas.bind("<ButtonPress-1>", self.on_press)  # 鼠标左键按下
        self.canvas.bind("<B1-Motion>", self.on_drag)  # 鼠标左键按住拖动

        # 绑定鼠标滚轮 (Windows)
        self.root.bind("<MouseWheel>", self.on_scroll)
        # 绑定鼠标滚轮 (Linux/Mac 兼容)
        self.root.bind("<Button-4>", lambda e: self.resize(10))
        self.root.bind("<Button-5>", lambda e: self.resize(-10))

        # 绑定回车键和双击保存
        self.root.bind("<Return>", self.save_and_exit)
        self.root.bind("<Double-Button-1>", self.save_and_exit)
        # 按 ESC 退出不保存
        self.root.bind("<Escape>", lambda e: self.root.destroy())

    def load_initial_pos(self):
        """尝试从 config.json 读取上次保存的坐标"""
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    minimap = config.get("MINIMAP", {})
                    if minimap:
                        self.x = minimap.get("left", 100)
                        self.y = minimap.get("top", 100)
                        self.size = minimap.get("width", 150)
            except Exception:
                pass

    def draw_ui(self):
        """绘制界面元素 (圆形准星和提示文字)"""
        self.canvas.delete("all")
        w = 3  # 边框厚度

        # 1. 绘制表示小地图边界的绿色圆圈
        self.canvas.create_oval(w, w, self.size - w, self.size - w, outline="#00FF00", width=w)

        # 2. 绘制十字准星中心辅助线
        self.canvas.create_line(0, self.size // 2, self.size, self.size // 2, fill="#00FF00", dash=(4, 4))
        self.canvas.create_line(self.size // 2, 0, self.size // 2, self.size, fill="#00FF00", dash=(4, 4))

        # 3. 绘制操作提示文字
        self.canvas.create_text(self.size // 2, 15, text="左键拖动 | 滚轮缩放", fill="white",
                                font=("Microsoft YaHei", 9, "bold"))
        self.canvas.create_text(self.size // 2, self.size - 15, text="按 回车/双击 保存", fill="yellow",
                                font=("Microsoft YaHei", 9, "bold"))

    def on_press(self, event):
        """记录鼠标按下的起始位置"""
        self.start_x = event.x
        self.start_y = event.y

    def on_drag(self, event):
        """计算鼠标拖动的偏移量并移动窗口"""
        dx = event.x - self.start_x
        dy = event.y - self.start_y
        self.x += dx
        self.y += dy
        self.root.geometry(f"{self.size}x{self.size}+{self.x}+{self.y}")

    def on_scroll(self, event):
        """处理鼠标滚轮放大缩小"""
        # Windows 的 delta 通常是 120 的倍数
        if event.delta > 0:
            self.resize(10)  # 向上滚放大
        else:
            self.resize(-10)  # 向下滚缩小

    def resize(self, delta):
        """改变窗口尺寸"""
        self.size += delta
        if self.size < 80:
            self.size = 80  # 限制最小不能低于 80 像素

        self.root.geometry(f"{self.size}x{self.size}+{self.x}+{self.y}")
        self.draw_ui()

    def save_and_exit(self, event=None):
        """将当前坐标写入 config.json 并退出"""
        config_data = {}
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
            except Exception:
                pass

        # 更新 JSON 字典中的 MINIMAP 节点
        config_data["MINIMAP"] = {
            "top": self.y,
            "left": self.x,
            "width": self.size,
            "height": self.size
        }

        # 写回文件
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, indent=4, ensure_ascii=False)

        print(f"✅ 小地图区域已成功保存: top={self.y}, left={self.x}, size={self.size}")
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = MinimapSelector(root)
    root.mainloop()