"""
天气API接口模块

整合和风天气API和weather.com.cn爬虫获取天气数据。
"""

import requests
import json
import time
import random
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from bs4 import BeautifulSoup


class WeatherAPI:
    """天气API接口类"""

    def __init__(self, api_domain: str = None, api_key: str = None):
        """
        初始化天气API接口

        Args:
            api_domain: 和风天气API域名
            api_key: API密钥
        """
        self.api_domain = api_domain
        self.api_key = api_key
        self.session = requests.Session()
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/json",
            "Referer": "https://dev.qweather.com/",
        }

    def get_weather_3d(self, location_id: str) -> Optional[Dict[str, Any]]:
        """
        获取3天天气预报（和风天气API）

        Args:
            location_id: 城市代码

        Returns:
            天气预报数据字典
        """
        url = f"https://{self.api_domain}/v7/weather/3d?location={location_id}&key={self.api_key}"
        try:
            response = requests.get(url, headers=self.headers, timeout=15)
            data = response.json()
            if data.get("code") == "200":
                return data.get("daily", [])
            return None
        except Exception:
            return None

    def get_weather_now(self, location_id: str) -> Optional[Dict[str, Any]]:
        """
        获取实况天气（和风天气API）

        Args:
            location_id: 城市代码

        Returns:
            实况天气数据
        """
        url = f"https://{self.api_domain}/v7/weather/now?location={location_id}&key={self.api_key}"
        try:
            response = requests.get(url, headers=self.headers, timeout=15)
            data = response.json()
            if data.get("code") == "200":
                return data.get("now", {})
            return None
        except Exception:
            return None

    def get_weather_warnings(self, location_id: str) -> List[Dict[str, str]]:
        """
        获取天气预警信息（和风天气API）

        Args:
            location_id: 城市代码

        Returns:
            预警信息列表
        """
        url = f"https://{self.api_domain}/v7/warning/now?location={location_id}&key={self.api_key}"
        try:
            response = requests.get(url, headers=self.headers, timeout=15)
            data = response.json()
            if data.get("code") == "200":
                warnings = []
                for w in data.get("warning", []):
                    if "地质" not in w.get("title", ""):
                        warnings.append({
                            "title": w.get("title", ""),
                            "type": w.get("typeName", "未知"),
                            "level": w.get("level", "未知"),
                            "text": w.get("text", ""),
                        })
                return warnings
            return []
        except Exception:
            return []

    def get_weather_from_website(self, city_code: str) -> Optional[str]:
        """
        从weather.com.cn爬取天气（备用方案）

        Args:
            city_code: 城市代码

        Returns:
            天气描述字符串
        """
        url = f"https://www.weather.com.cn/weather/{city_code}.shtml"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Referer": "https://www.weather.com.cn/",
        }
        try:
            time.sleep(random.uniform(0.5, 1.5))
            response = requests.get(url, headers=headers, timeout=15)
            response.encoding = "utf-8"
            soup = BeautifulSoup(response.text, "html.parser")
            weather_list = soup.find("ul", class_="t clearfix")
            if weather_list:
                items = weather_list.find_all("li")
                if items:
                    wea = items[0].find("p", class_="wea")
                    tem = items[0].find("p", class_="tem")
                    if wea and tem:
                        weather = wea.get_text(strip=True)
                        temp = tem.get_text(strip=True).replace("高温 ", "").replace("低温 ", "").replace(" ", "")
                        return f"{weather} {temp}"
            return None
        except Exception:
            return None

    def get_city_name(self, location_id: str, city_map: Dict[str, str]) -> str:
        """
        获取城市名称

        Args:
            location_id: 城市代码
            city_map: 城市代码到名称的映射

        Returns:
            城市名称
        """
        return city_map.get(location_id, f"城市{location_id}")

    def get_all_cities_weather(
        self, cities: Dict[str, str], days: int = 3
    ) -> List[Dict[str, Any]]:
        """
        获取所有城市的天气数据

        Args:
            cities: 城市代码到名称的映射
            days: 预报天数

        Returns:
            所有城市的天气数据列表
        """
        results = []
        for city_code, city_name in cities.items():
            # 获取3天预报
            forecast = self.get_weather_3d(city_code)

            # 获取实况天气
            now = self.get_weather_now(city_code)

            # 获取预警
            warnings = self.get_weather_warnings(city_code)

            city_data = {
                "code": city_code,
                "name": city_name,
                "forecast": forecast if forecast else [],
                "now": now,
                "warnings": warnings,
            }
            results.append(city_data)

            # 请求间隔
            time.sleep(0.3)

        return results


