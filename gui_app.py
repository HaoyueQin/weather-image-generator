"""
天气预报播报图片生成器 - GUI版本
打开应用自动生成图片，支持一键复制到剪贴板
"""

import os
import sys
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from PIL import Image, ImageTk
import io

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import API_DOMAIN, API_KEY, CITIES, COLORS, IMAGE_WIDTH, FONT_PATH
from src.weather_api import WeatherAPI
from src.image_generator import WeatherImageGenerator
from src.date_utils import get_upcoming_events, format_date_info


class WeatherApp:
    def __init__(self, root):
        self.root = root
        self.root.title("天气预报播报图片生成器")
        self.root.geometry("1200x800")
        self.root.configure(bg="#f5f5f7")
        
        # 当前图片
        self.current_image = None
        self.current_image_path = None
        
        # 创建界面
        self.create_widgets()
        
        # 自动生成图片
        self.generate_weather_image()
    
    def create_widgets(self):
        # 标题栏
        title_frame = tk.Frame(self.root, bg="#ffffff", height=60)
        title_frame.pack(fill=tk.X, padx=0, pady=0)
        title_frame.pack_propagate(False)
        
        title_label = tk.Label(title_frame, text="天气预报播报图片生成器", 
                              font=("Microsoft YaHei", 20, "bold"),
                              bg="#ffffff", fg="#1d1d1f")
        title_label.pack(side=tk.LEFT, padx=20, pady=10)
        
        # 按钮区域
        btn_frame = tk.Frame(title_frame, bg="#ffffff")
        btn_frame.pack(side=tk.RIGHT, padx=20)
        
        # 刷新按钮
        refresh_btn = tk.Button(btn_frame, text="刷新", command=self.generate_weather_image,
                               bg="#0066cc", fg="white", font=("Microsoft YaHei", 12),
                               relief="flat", padx=20, pady=8, cursor="hand2")
        refresh_btn.pack(side=tk.LEFT, padx=5)
        
        # 复制到剪贴板按钮
        copy_btn = tk.Button(btn_frame, text="复制到剪贴板", command=self.copy_to_clipboard,
                            bg="#00843d", fg="white", font=("Microsoft YaHei", 12),
                            relief="flat", padx=20, pady=8, cursor="hand2")
        copy_btn.pack(side=tk.LEFT, padx=5)
        
        # 保存按钮
        save_btn = tk.Button(btn_frame, text="保存图片", command=self.save_image,
                            bg="#7a7a7a", fg="white", font=("Microsoft YaHei", 12),
                            relief="flat", padx=20, pady=8, cursor="hand2")
        save_btn.pack(side=tk.LEFT, padx=5)
        
        # 主内容区域
        main_frame = tk.Frame(self.root, bg="#f5f5f7")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # 图片显示区域
        self.image_frame = tk.Frame(main_frame, bg="#ffffff", relief="solid", bd=1)
        self.image_frame.pack(fill=tk.BOTH, expand=True)
        
        # 图片标签
        self.image_label = tk.Label(self.image_frame, bg="#ffffff")
        self.image_label.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 状态栏
        status_frame = tk.Frame(self.root, bg="#ffffff", height=40)
        status_frame.pack(fill=tk.X, padx=0, pady=0)
        status_frame.pack_propagate(False)
        
        self.status_label = tk.Label(status_frame, text="就绪", 
                                    font=("Microsoft YaHei", 10),
                                    bg="#ffffff", fg="#7a7a7a")
        self.status_label.pack(side=tk.LEFT, padx=20, pady=10)
        
        self.time_label = tk.Label(status_frame, text="", 
                                  font=("Microsoft YaHei", 10),
                                  bg="#ffffff", fg="#7a7a7a")
        self.time_label.pack(side=tk.RIGHT, padx=20, pady=10)
    
    def generate_weather_image(self):
        """生成天气图片"""
        self.status_label.config(text="正在生成图片...")
        self.root.update()
        
        try:
            # 初始化API
            api = WeatherAPI(api_domain=API_DOMAIN, api_key=API_KEY)
            
            # 获取天气数据
            cities_weather = api.get_all_cities_weather(CITIES)
            
            # 获取日期信息
            now = datetime.now()
            date_info = format_date_info(now)
            
            # 获取未来节日
            upcoming_events = get_upcoming_events(now, num_events=5)
            
            # 初始化图片生成器
            config = {
                "width": IMAGE_WIDTH,
                "colors": COLORS,
                "font_path": FONT_PATH,
            }
            generator = WeatherImageGenerator(config)
            
            # 生成图片
            output_path = os.path.join("output", f"weather_{now.strftime('%Y%m%d_%H%M%S')}.png")
            os.makedirs("output", exist_ok=True)
            
            success = generator.generate_image(date_info, cities_weather, upcoming_events, output_path)
            
            if success:
                self.current_image_path = output_path
                self.display_image(output_path)
                self.status_label.config(text=f"图片已生成: {os.path.basename(output_path)}")
                self.time_label.config(text=f"更新时间: {now.strftime('%Y-%m-%d %H:%M:%S')}")
            else:
                self.status_label.config(text="图片生成失败")
                messagebox.showerror("错误", "图片生成失败")
                
        except Exception as e:
            self.status_label.config(text=f"错误: {str(e)}")
            messagebox.showerror("错误", f"生成图片时出错:\n{str(e)}")
    
    def display_image(self, image_path):
        """显示图片"""
        try:
            # 打开图片
            image = Image.open(image_path)
            
            # 计算缩放比例以适应窗口
            frame_width = self.image_frame.winfo_width()
            frame_height = self.image_frame.winfo_height()
            
            if frame_width > 1 and frame_height > 1:
                # 计算缩放比例
                ratio = min(frame_width / image.width, frame_height / image.height)
                new_width = int(image.width * ratio)
                new_height = int(image.height * ratio)
                
                # 缩放图片
                image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # 转换为PhotoImage
            self.current_image = ImageTk.PhotoImage(image)
            
            # 显示图片
            self.image_label.config(image=self.current_image)
            
        except Exception as e:
            print(f"显示图片失败: {e}")
    
    def copy_to_clipboard(self):
        """复制图片到剪贴板"""
        if not self.current_image_path:
            messagebox.showwarning("警告", "请先生成图片")
            return
        
        try:
            # 打开图片
            image = Image.open(self.current_image_path)
            
            # 复制到剪贴板
            self.root.clipboard_clear()
            
            # 使用win32clipboard复制图片到剪贴板
            try:
                import win32clipboard
                import win32con
                
                # 保存图片到临时文件
                temp_path = os.path.join("output", "temp_clipboard.png")
                image.save(temp_path)
                
                # 打开剪贴板
                win32clipboard.OpenClipboard()
                win32clipboard.EmptyClipboard()
                
                # 读取图片数据
                with open(temp_path, 'rb') as f:
                    image_data = f.read()
                
                # 设置剪贴板数据
                win32clipboard.SetClipboardData(win32con.CF_DIB, image_data)
                win32clipboard.CloseClipboard()
                
                # 删除临时文件
                os.remove(temp_path)
                
                self.status_label.config(text="图片已复制到剪贴板")
                messagebox.showinfo("成功", "图片已复制到剪贴板")
                
            except ImportError:
                # 如果没有win32clipboard，使用其他方法
                # 尝试使用pyperclip
                try:
                    import pyperclip
                    pyperclip.copy(f"图片路径: {os.path.abspath(self.current_image_path)}")
                    self.status_label.config(text="图片路径已复制到剪贴板")
                    messagebox.showinfo("成功", "图片路径已复制到剪贴板")
                except ImportError:
                    # 最后尝试使用tkinter的clipboard
                    self.root.clipboard_clear()
                    self.root.clipboard_append(f"图片路径: {os.path.abspath(self.current_image_path)}")
                    self.status_label.config(text="图片路径已复制到剪贴板")
                    messagebox.showinfo("成功", "图片路径已复制到剪贴板")
                    
        except Exception as e:
            self.status_label.config(text=f"复制失败: {str(e)}")
            messagebox.showerror("错误", f"复制到剪贴板时出错:\n{str(e)}")
    
    def save_image(self):
        """保存图片"""
        if not self.current_image_path:
            messagebox.showwarning("警告", "请先生成图片")
            return
        
        try:
            from tkinter import filedialog
            
            # 打开文件对话框
            file_path = filedialog.asksaveasfilename(
                defaultextension=".png",
                filetypes=[("PNG files", "*.png"), ("All files", "*.*")],
                initialfile=f"weather_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            )
            
            if file_path:
                # 复制文件
                import shutil
                shutil.copy2(self.current_image_path, file_path)
                self.status_label.config(text=f"图片已保存到: {file_path}")
                messagebox.showinfo("成功", f"图片已保存到:\n{file_path}")
                
        except Exception as e:
            self.status_label.config(text=f"保存失败: {str(e)}")
            messagebox.showerror("错误", f"保存图片时出错:\n{str(e)}")


def main():
    # 检查依赖
    try:
        import tkinter
        from PIL import Image, ImageTk
    except ImportError as e:
        print(f"缺少依赖: {e}")
        print("请运行: pip install Pillow")
        return
    
    # 创建主窗口
    root = tk.Tk()
    app = WeatherApp(root)
    
    # 绑定窗口大小变化事件
    def on_resize(event):
        if app.current_image_path:
            app.display_image(app.current_image_path)
    
    root.bind("<Configure>", on_resize)
    
    # 运行应用
    root.mainloop()


if __name__ == "__main__":
    main()