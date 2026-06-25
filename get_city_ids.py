"""
获取和风天气全部支持城市的 LocationID
输出城市ID参考表到 CITY_IDS.md

用法：python get_city_ids.py
"""
import requests
import csv
import time
import os
import json
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv('API_KEY')
API_DOMAIN = os.getenv('API_DOMAIN', 'nk7h2q8uut.re.qweatherapi.com')

# 省级行政区列表
PROVINCES = [
    '101010100', '101020100', '101030100', '101040100',  # 北京、天津、上海、重庆（直接用ID）
    '河北', '山西', '辽宁', '吉林', '黑龙江',
    '江苏', '浙江', '安徽', '福建', '江西', '山东',
    '河南', '湖北', '湖南', '广东', '海南',
    '四川', '贵州', '云南', '陕西', '甘肃', '青海',
    '台湾', '内蒙古', '广西', '西藏', '宁夏', '新疆',
    '香港', '澳门'
]


def search_city_by_id(loc_id: str) -> list:
    """通过ID查询城市"""
    url = f'https://{API_DOMAIN}/geo/v2/city/lookup'
    params = {'location': loc_id, 'key': API_KEY, 'number': 10}
    resp = requests.get(url, params=params, timeout=10)
    resp.encoding = 'utf-8'
    try:
        data = resp.json()
        if data.get('code') == '200':
            return data.get('location', [])
    except Exception:
        pass
    return []


def search_city_by_name(keyword: str) -> list:
    """通过名称查询城市"""
    url = f'https://{API_DOMAIN}/geo/v2/city/lookup'
    params = {'location': keyword, 'key': API_KEY, 'range': 'cn', 'number': 20}
    resp = requests.get(url, params=params, timeout=10)
    resp.encoding = 'utf-8'
    try:
        data = resp.json()
        if data.get('code') == '200':
            return data.get('location', [])
    except Exception:
        pass
    return []


def get_all_cities() -> list:
    """获取所有城市"""
    all_cities = []
    seen_ids = set()

    print(f"开始遍历 {len(PROVINCES)} 个省级行政区...")
    
    for province in PROVINCES:
        if province.isdigit():
            # 直接通过ID查询
            locations = search_city_by_id(province)
        else:
            # 通过名称查询
            print(f"  正在查询: {province}...")
            locations = search_city_by_name(province)
        
        for loc in locations:
            loc_id = loc['id']
            if loc_id in seen_ids:
                continue
            seen_ids.add(loc_id)
            
            all_cities.append({
                'id': loc_id,
                'name': loc.get('name', ''),
                'adm2': loc.get('adm2', ''),
                'adm1': loc.get('adm1', ''),
                'lat': loc.get('lat', ''),
                'lon': loc.get('lon', '')
            })
        
        time.sleep(0.3)  # API 限速
    
    # 按省份和城市排序
    all_cities.sort(key=lambda x: (x['adm1'], x['adm2'], x['name']))
    return all_cities


def save_csv(cities: list, filename: str = 'city_ids.csv'):
    """保存为 CSV"""
    with open(filename, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['id', 'name', 'adm2', 'adm1', 'lat', 'lon'])
        writer.writeheader()
        writer.writerows(cities)
    print(f"\n已保存 {len(cities)} 个城市到 {filename}")


def save_markdown(cities: list, filename: str = 'CITY_IDS.md'):
    """保存为 Markdown 参考表"""
    with open(filename, 'w', encoding='utf-8') as f:
        f.write("# 和风天气城市 LocationID 参考表\n\n")
        f.write(f"共 {len(cities)} 个城市/区县\n\n")
        f.write("## 使用方法\n\n")
        f.write("将 `id` 列的值复制到 `config.py` 的 `CITIES` 字典中：\n\n")
        f.write("```python\nCITIES = {\n    '101010100': '北京',\n    # ...\n}\n```\n\n")
        
        # 按省份分组
        current_province = None
        for city in cities:
            if city['adm1'] != current_province:
                if current_province:
                    f.write("\n")
                current_province = city['adm1']
                f.write(f"## {current_province}\n\n")
                f.write("| LocationID | 城市 | 区县 | 经度 | 纬度 |\n")
                f.write("|------------|------|------|------|------|\n")
            
            f.write(f"| {city['id']} | {city['adm2']} | {city['name']} | {city['lon']} | {city['lat']} |\n")
    
    print(f"已保存参考表到 {filename}")


if __name__ == '__main__':
    print("和风天气城市ID获取工具\n")
    
    if not API_KEY:
        print("错误: 请在 .env 文件中配置 API_KEY")
        exit(1)
    
    cities = get_all_cities()
    print(f"\n共获取 {len(cities)} 个城市/区县")
    
    save_csv(cities)
    save_markdown(cities)
    
    # 输出前 10 个作为示例
    print("\n前 10 个城市:")
    for city in cities[:10]:
        print(f"  {city['id']}: {city['adm1']} {city['adm2']} {city['name']}")
