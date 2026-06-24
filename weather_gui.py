"""
天气预报播报图片生成器 - GUI应用
"""

import os
import sys
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
from PIL import Image, ImageTk
import threading
import tempfile


def get_exe_dir():
    """获取exe所在的目录"""
    try:
        return os.path.dirname(sys.executable)
    except:
        return os.path.dirname(os.path.abspath(__file__))


def load_local_config():
    """从 .env 文件加载 API Key"""
    from dotenv import load_dotenv
    # 优先从项目根目录加载 .env，其次从 exe 同目录
    exe_dir = get_exe_dir()
    env_path = os.path.join(exe_dir, ".env")
    if not os.path.exists(env_path):
        env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
    load_dotenv(env_path, override=True)
    return os.getenv("API_KEY", "")


def save_local_config(api_key):
    """保存API密钥到 .env 文件"""
    exe_dir = get_exe_dir()
    env_path = os.path.join(exe_dir, ".env")

    try:
        with open(env_path, 'w', encoding='utf-8') as f:
            f.write(f'API_KEY={api_key}\n')
        return True
    except Exception as e:
        return False


def copy_image_to_clipboard(image_path):
    """复制图片到剪贴板"""
    try:
        import win32clipboard
        import win32con
        from PIL import Image as PILImage
        
        image = PILImage.open(image_path)
        image = image.convert("RGB")
        
        temp_dir = tempfile.gettempdir()
        temp_bmp = os.path.join(temp_dir, "clipboard_weather.bmp")
        image.save(temp_bmp, "BMP")
        
        with open(temp_bmp, 'rb') as f:
            f.read(14)
            bmp_data = f.read()
        
        win32clipboard.OpenClipboard()
        win32clipboard.EmptyClipboard()
        win32clipboard.SetClipboardData(win32con.CF_DIB, bmp_data)
        win32clipboard.CloseClipboard()
        
        try:
            os.remove(temp_bmp)
        except:
            pass
        
        return True
    except Exception as e:
        return False


class WeatherApp:
    def __init__(self, root):
        self.root = root
        self.root.title("天气预报播报图片生成器")
        
        # 初始窗口：竖向比例
        screen_w = root.winfo_screenwidth()
        screen_h = root.winfo_screenheight()
        init_w = 500
        init_h = min(900, screen_h - 100)
        x = (screen_w - init_w) // 2
        y = (screen_h - init_h) // 2
        self.root.geometry(f"{init_w}x{init_h}+{x}+{y}")
        self.root.configure(bg="#f5f5f7")
        self.root.minsize(400, 600)
        
        self.current_image = None
        self.current_image_path = None
        self.current_image_original = None
        
        self.create_widgets()
        self.root.after(500, self.generate_weather_image)
    
    def create_widgets(self):
        # 标题栏
        title_frame = tk.Frame(self.root, bg="#ffffff", height=55)
        title_frame.pack(fill=tk.X)
        title_frame.pack_propagate(False)
        
        tk.Label(title_frame, text="天气预报播报图片生成器", 
                font=("Microsoft YaHei", 16, "bold"),
                bg="#ffffff", fg="#1d1d1f").pack(side=tk.LEFT, padx=15, pady=12)
        
        # 按钮
        btn_frame = tk.Frame(title_frame, bg="#ffffff")
        btn_frame.pack(side=tk.RIGHT, padx=15)
        
        tk.Button(btn_frame, text="刷新", command=self.generate_weather_image,
                 bg="#0066cc", fg="white", font=("Microsoft YaHei", 10),
                 relief="flat", width=6, pady=6, cursor="hand2").pack(side=tk.LEFT, padx=5)
        
        tk.Button(btn_frame, text="复制", command=self.copy_to_clipboard,
                 bg="#00843d", fg="white", font=("Microsoft YaHei", 10),
                 relief="flat", width=6, pady=6, cursor="hand2").pack(side=tk.LEFT, padx=5)
        
        tk.Button(btn_frame, text="保存", command=self.save_image,
                 bg="#7a7a7a", fg="white", font=("Microsoft YaHei", 10),
                 relief="flat", width=6, pady=6, cursor="hand2").pack(side=tk.LEFT, padx=5)
        
        # 图片区域
        self.image_frame = tk.Frame(self.root, bg="#ffffff")
        self.image_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.canvas = tk.Canvas(self.image_frame, bg="#ffffff", highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.canvas.bind("<Configure>", self.on_canvas_resize)
        
        # 状态栏
        status_frame = tk.Frame(self.root, bg="#ffffff", height=35)
        status_frame.pack(fill=tk.X)
        status_frame.pack_propagate(False)
        
        self.status_label = tk.Label(status_frame, text="正在启动...", 
                                    font=("Microsoft YaHei", 9),
                                    bg="#ffffff", fg="#7a7a7a")
        self.status_label.pack(side=tk.LEFT, padx=15, pady=8)
        
        self.time_label = tk.Label(status_frame, text="", 
                                  font=("Microsoft YaHei", 9),
                                  bg="#ffffff", fg="#7a7a7a")
        self.time_label.pack(side=tk.RIGHT, padx=15, pady=8)
    
    def on_canvas_resize(self, event):
        if self.current_image_original:
            self.display_image_on_canvas()
    
    def display_image_on_canvas(self):
        if not self.current_image_original:
            return
        
        canvas_w = self.canvas.winfo_width()
        canvas_h = self.canvas.winfo_height()
        if canvas_w <= 1 or canvas_h <= 1:
            return
        
        img_w, img_h = self.current_image_original.size
        ratio = min(canvas_w / img_w, canvas_h / img_h)
        new_w = int(img_w * ratio)
        new_h = int(img_h * ratio)
        
        resized = self.current_image_original.resize((new_w, new_h), Image.Resampling.LANCZOS)
        self.current_image = ImageTk.PhotoImage(resized)
        
        self.canvas.delete("all")
        x = (canvas_w - new_w) // 2
        y = (canvas_h - new_h) // 2
        self.canvas.create_image(x, y, anchor="nw", image=self.current_image)
    
    def generate_weather_image(self):
        self.status_label.config(text="正在生成图片...")
        self.root.update()
        
        def generate_in_thread():
            try:
                from src.weather_api import WeatherAPI
                from src.image_generator import WeatherImageGenerator
                from src.date_utils import get_upcoming_events, format_date_info
                
                try:
                    from config import API_DOMAIN, CITIES, COLORS, IMAGE_WIDTH, FONT_PATH
                except ImportError:
                    API_DOMAIN = "nk7h2q8uut.re.qweatherapi.com"
                    CITIES = {}
                    COLORS = {}
                    IMAGE_WIDTH = 1440
                    FONT_PATH = None
                
                API_KEY = load_local_config()
                
                if not API_KEY:
                    # 弹出配置对话框
                    def show_config_dialog():
                        self.show_api_config_dialog()
                    self.root.after(0, show_config_dialog)
                    return
                
                api = WeatherAPI(api_domain=API_DOMAIN, api_key=API_KEY)
                
                if not CITIES:
                    self.root.after(0, lambda: self.status_label.config(text="未配置城市"))
                    return
                
                cities_weather = api.get_all_cities_weather(CITIES)
                now = datetime.now()
                date_info = format_date_info(now)
                upcoming_events = get_upcoming_events(now, num_events=5)
                
                config = {"width": IMAGE_WIDTH, "colors": COLORS, "font_path": FONT_PATH}
                generator = WeatherImageGenerator(config)
                
                output_dir = "output"
                os.makedirs(output_dir, exist_ok=True)
                output_path = os.path.join(output_dir, f"weather_{now.strftime('%Y%m%d_%H%M%S')}.png")
                
                success = generator.generate_image(date_info, cities_weather, upcoming_events, output_path)
                
                if success:
                    self.current_image_path = output_path
                    self.current_image_original = Image.open(output_path)
                    self.root.after(0, self.display_image_on_canvas)
                    self.root.after(0, lambda: self.status_label.config(text=f"已生成: {os.path.basename(output_path)}"))
                    self.root.after(0, lambda: self.time_label.config(text=now.strftime('%Y-%m-%d %H:%M:%S')))
                else:
                    self.root.after(0, lambda: self.status_label.config(text="图片生成失败"))
                    
            except Exception as e:
                self.root.after(0, lambda: self.status_label.config(text=f"错误: {str(e)}"))
        
        thread = threading.Thread(target=generate_in_thread, daemon=True)
        thread.start()
    
    def show_api_config_dialog(self):
        """显示API密钥配置对话框"""
        dialog = tk.Toplevel(self.root)
        dialog.title("首次使用配置")
        dialog.geometry("500x300")
        dialog.configure(bg="#f5f5f7")
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()
        
        # 标题
        tk.Label(dialog, text="配置和风天气API密钥", 
                font=("Microsoft YaHei", 16, "bold"),
                bg="#f5f5f7", fg="#1d1d1f").pack(pady=(20, 10))
        
        # 说明
        tk.Label(dialog, text="1. 访问 https://dev.qweather.com/ 注册并创建API Key",
                font=("Microsoft YaHei", 11), bg="#f5f5f7", fg="#7a7a7a").pack(anchor="w", padx=40)
        tk.Label(dialog, text="2. 将API Key粘贴到下方输入框",
                font=("Microsoft YaHei", 11), bg="#f5f5f7", fg="#7a7a7a").pack(anchor="w", padx=40, pady=(0, 10))
        
        # 输入框
        tk.Label(dialog, text="API Key:", font=("Microsoft YaHei", 11), bg="#f5f5f7").pack(anchor="w", padx=40)
        api_entry = tk.Entry(dialog, font=("Microsoft YaHei", 12), width=40, relief="solid", bd=1)
        api_entry.pack(padx=40, pady=(5, 15), fill=tk.X)
        api_entry.focus_set()
        
        # 按钮
        btn_frame = tk.Frame(dialog, bg="#f5f5f7")
        btn_frame.pack(fill=tk.X, padx=40)
        
        def on_confirm():
            api_key = api_entry.get().strip()
            if api_key:
                save_local_config(api_key)
                dialog.destroy()
                self.generate_weather_image()
            else:
                messagebox.showwarning("提示", "请输入API密钥", parent=dialog)
        
        def on_skip():
            dialog.destroy()
            self.status_label.config(text="未配置API密钥，无法获取天气数据")
        
        tk.Button(btn_frame, text="确认", command=on_confirm,
                 bg="#0066cc", fg="white", font=("Microsoft YaHei", 11),
                 relief="flat", padx=25, pady=6).pack(side=tk.RIGHT, padx=5)
        
        tk.Button(btn_frame, text="稍后配置", command=on_skip,
                 bg="#7a7a7a", fg="white", font=("Microsoft YaHei", 11),
                 relief="flat", padx=25, pady=6).pack(side=tk.RIGHT, padx=5)
        
        api_entry.bind("<Return>", lambda e: on_confirm())
    
    def copy_to_clipboard(self):
        if not self.current_image_path:
            messagebox.showwarning("警告", "请先生成图片")
            return
        
        self.status_label.config(text="正在复制到剪贴板...")
        self.root.update()
        
        if copy_image_to_clipboard(self.current_image_path):
            self.status_label.config(text="已复制到剪贴板")
            messagebox.showinfo("成功", "图片已复制到剪贴板\n可直接粘贴到微信、QQ等应用")
        else:
            self.root.clipboard_clear()
            self.root.clipboard_append(os.path.abspath(self.current_image_path))
            self.status_label.config(text="已复制图片路径")
            messagebox.showinfo("提示", "图片路径已复制到剪贴板")
    
    def save_image(self):
        if not self.current_image_path:
            messagebox.showwarning("警告", "请先生成图片")
            return
        
        try:
            file_path = filedialog.asksaveasfilename(
                defaultextension=".png",
                filetypes=[("PNG图片", "*.png"), ("所有文件", "*.*")],
                initialfile=f"天气预报_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            )
            if file_path:
                import shutil
                shutil.copy2(self.current_image_path, file_path)
                self.status_label.config(text=f"已保存: {os.path.basename(file_path)}")
        except Exception as e:
            self.status_label.config(text=f"保存失败: {str(e)}")


def main():
    try:
        import tkinter
        from PIL import Image, ImageTk
    except ImportError as e:
        print(f"缺少依赖: {e}")
        print("请安装: pip install Pillow")
        input("按回车键退出...")
        return
    
    root = tk.Tk()
    app = WeatherApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()