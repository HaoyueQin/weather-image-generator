"""
天气预报播报图片生成器

一个简单的天气预报播报图片生成工具，可以获取多个城市的实时天气信息，
并生成精美的天气预报播报图片。
"""

__version__ = "0.1.0"

from .weather_api import WeatherAPI
from .image_generator import WeatherImageGenerator
from .date_utils import get_upcoming_events, format_date_info