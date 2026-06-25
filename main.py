"""
天气预报播报图片生成器

主程序入口：获取天气数据并生成图片。
"""

import os
import sys
from datetime import datetime

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import API_DOMAIN, API_KEY, CITIES, COLORS, IMAGE_WIDTH, FONT_PATH
from src.weather_api import WeatherAPI
from src.image_generator import WeatherImageGenerator
from src.date_utils import get_upcoming_events, format_date_info


def main():
    """主函数"""
    print("=" * 60)
    print("天气预报播报图片生成器")
    print("=" * 60)

    # 初始化API
    api = WeatherAPI(api_domain=API_DOMAIN, api_key=API_KEY)

    # 获取所有城市的天气数据
    print(f"\n正在获取 {len(CITIES)} 个城市的天气数据...")
    cities_weather = api.get_all_cities_weather(CITIES)
    print(f"[OK] 成功获取 {len(cities_weather)} 个城市的数据")

    # 统计预警数量
    warning_count = sum(len(c.get("warnings", [])) for c in cities_weather)
    if warning_count > 0:
        print(f"[!] 发现 {warning_count} 条天气预警")

    # 获取日期信息
    now = datetime.now()
    date_info = format_date_info(now)
    print(f"\n{date_info['solar_date']} {date_info['weekday']}")
    if date_info.get("solar_term"):
        print(f"   节气: {date_info['solar_term']}")
    if date_info.get("festival"):
        print(f"   节日: {date_info['festival']}")

    # 获取未来节日/节气
    upcoming = get_upcoming_events(now, num_events=5)
    print(f"\n未来节日/节气:")
    for event_date, event_name in upcoming:
        days_left = (event_date.replace(hour=0, minute=0, second=0) - now.replace(hour=0, minute=0, second=0)).days
        print(f"   {event_name}: {event_date.strftime('%m月%d日')} ({days_left}天后)")

    # 初始化图片生成器
    config = {
        "width": IMAGE_WIDTH,
        "colors": COLORS,
        "font_path": FONT_PATH,
    }
    generator = WeatherImageGenerator(config)

    # 生成图片
    output_dir = os.path.join("output", now.strftime("%Y_%m"))
    os.makedirs(output_dir, exist_ok=True)
    output_filename = f"weather_{now.strftime('%Y_%m_%d')}.png"
    output_path = os.path.join(output_dir, output_filename)

    print(f"\n正在生成图片...")
    success = generator.generate_image(date_info, cities_weather, upcoming, output_path)

    if success:
        print(f"图片生成成功: {output_path}")
        print(f"文件大小: {os.path.getsize(output_path) / 1024:.1f} KB")
    else:
        print("图片生成失败")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
