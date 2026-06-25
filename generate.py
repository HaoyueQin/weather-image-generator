"""
天气预报图片生成 + 复制到剪贴板

用法：python generate.py
生成图片并自动复制到剪贴板，可直接粘贴到微信/QQ等。
"""

import os
import sys
from datetime import datetime

from config import API_KEY, API_DOMAIN, CITIES, COLORS, IMAGE_WIDTH, FONT_PATH
from src.weather_api import WeatherAPI
from src.image_generator import WeatherImageGenerator
from src.date_utils import format_date_info, get_upcoming_events


def copy_image_to_clipboard(image_path: str) -> bool:
    """将图片复制到 Windows 剪贴板"""
    try:
        import win32clipboard
        import win32con
        from PIL import Image as PILImage

        img = PILImage.open(image_path)
        output = img.convert("RGB")
        import io
        data = io.BytesIO()
        output.save(data, "BMP")
        # BMP 文件头 14 字节 + DIB 头需要跳过
        bmp_data = data.getvalue()[14:]

        win32clipboard.OpenClipboard()
        win32clipboard.EmptyClipboard()
        win32clipboard.SetClipboardData(win32con.CF_DIB, bmp_data)
        win32clipboard.CloseClipboard()
        return True
    except ImportError:
        print("  [提示] 未安装 pywin32，跳过剪贴板复制")
        print("  安装命令: pip install pywin32")
        return False
    except Exception as e:
        print(f"  [错误] 复制到剪贴板失败: {e}")
        return False


def main():
    print("=" * 50)
    print("  天气预报图片生成器")
    print("=" * 50)
    print()

    if not API_KEY:
        print("[错误] 未配置 API Key，请在 .env 文件中设置 API_KEY")
        sys.exit(1)

    # 获取天气数据
    print(f"[1/3] 获取 {len(CITIES)} 个城市天气数据...")
    api = WeatherAPI(api_domain=API_DOMAIN, api_key=API_KEY)
    cities_weather = api.get_all_cities_weather(CITIES)
    print(f"      完成，获取到 {len(cities_weather)} 个城市数据")

    # 生成日期信息
    now = datetime.now()
    date_info = format_date_info(now)
    upcoming = get_upcoming_events(now, 5)

    # 生成图片
    print("[2/3] 生成天气预报图片...")
    config = {"width": IMAGE_WIDTH, "colors": COLORS, "font_path": FONT_PATH}
    gen = WeatherImageGenerator(config)

    month_dir = os.path.join("output", now.strftime("%Y_%m"))
    os.makedirs(month_dir, exist_ok=True)
    filename = f"weather_{now.strftime('%Y_%m_%d')}.png"
    output_path = os.path.join(month_dir, filename)

    success = gen.generate_image(date_info, cities_weather, upcoming, output_path)

    if not success:
        print("[错误] 图片生成失败")
        sys.exit(1)

    fsize = os.path.getsize(output_path)
    print(f"      保存至: {output_path}")
    print(f"      文件大小: {fsize / 1024:.0f} KB")

    # 复制到剪贴板
    print("[3/3] 复制到剪贴板...")
    if copy_image_to_clipboard(output_path):
        print("      已复制！可直接粘贴到微信/QQ/钉钉等")
    print()
    print("=" * 50)
    print("  完成！按任意键退出...")
    print("=" * 50)


if __name__ == "__main__":
    main()
