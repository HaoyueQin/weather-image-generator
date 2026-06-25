"""
城市管理工具 - 交互式增删城市

功能：
- 模糊搜索城市（支持"北京市昌平区"、"昌平"、"北京昌平"等形式）
- 添加/删除城市到 config.py
- 列出当前已添加的城市
- 从和风天气 API 在线搜索

用法：python manage_cities.py
"""
import re
import os
import csv
import sys
from pathlib import Path

# 项目根目录
ROOT_DIR = Path(__file__).parent
CONFIG_PATH = ROOT_DIR / "config.py"
CSV_PATH = ROOT_DIR / "city_ids.csv"

# 颜色输出
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
CYAN = "\033[96m"
RESET = "\033[0m"
BOLD = "\033[1m"


def load_city_database() -> list:
    """加载城市数据库"""
    cities = []
    if not CSV_PATH.exists():
        print(f"{RED}错误: 找不到 city_ids.csv 文件{RESET}")
        print(f"请先运行 get_city_ids_v2.py 生成城市数据库")
        return cities

    with open(CSV_PATH, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            cities.append({
                'id': row['id'],
                'name': row['name'],
                'adm2': row.get('adm2', ''),
                'adm1': row.get('adm1', ''),
            })
    return cities


def normalize_text(text: str) -> str:
    """规范化文本：去除空格、标点、"市"/"区"/"县"等后缀"""
    # 去除空格和常见标点
    text = re.sub(r'[\s\-_,.，。、]+', '', text)
    # 去除常见后缀（但保留核心名称）
    # 注意：不能全部去除，否则"北京市"和"北京"会混淆
    return text.lower()


def fuzzy_match(query: str, cities: list) -> list:
    """模糊匹配城市
    
    支持的输入形式：
    - "昌平" -> 匹配 name="昌平"
    - "北京昌平" -> 匹配 adm2="北京", name="昌平"
    - "北京市昌平区" -> 匹配 adm2="北京", name="昌平"
    - "昌平区" -> 匹配 name="昌平"
    - "山东曲阜" -> 匹配 adm1="山东", name="曲阜"
    """
    # 定义常见后缀
    suffixes = ['市', '区', '县', '镇', '省', '地区', '州', '盟']
    
    def remove_suffix(text: str) -> str:
        """去除常见后缀"""
        for suffix in suffixes:
            if text.endswith(suffix) and len(text) > len(suffix):
                return text[:-len(suffix)]
        return text
    
    def remove_all_suffixes(text: str) -> str:
        """去除所有常见后缀"""
        changed = True
        while changed:
            changed = False
            for suffix in suffixes:
                if text.endswith(suffix) and len(text) > len(suffix):
                    text = text[:-len(suffix)]
                    changed = True
                    break
        return text
    
    def is_city_type(city: dict) -> bool:
        """判断是否为地级市（而非区县）"""
        # 地级市的特征：name == adm2 或者 name 以"市"结尾且 adm2 == name
        city_name = city.get('name', '')
        adm2 = city.get('adm2', '')
        return city_name == adm2 or (city_name.endswith('市') and city_name[:-1] == adm2)
    
    query = normalize_text(query)
    query_no_suffix = remove_suffix(query)
    query_no_all_suffixes = remove_all_suffixes(query)
    results = []
    
    for city in cities:
        city_name = normalize_text(city['name'])
        city_name_no_suffix = remove_suffix(city_name)
        adm2 = normalize_text(city['adm2'])
        adm2_no_suffix = remove_suffix(adm2)
        adm1 = normalize_text(city['adm1'])
        adm1_no_suffix = remove_suffix(adm1)
        
        # 计算完整名称
        full_name = adm1 + adm2 + city_name
        full_name_no_suffix = adm1_no_suffix + adm2_no_suffix + city_name_no_suffix
        
        # 基础分数
        base_score = 0
        matched = False
        
        # 1. 精确匹配完整路径（最高优先级）
        if query == full_name or query_no_suffix == full_name_no_suffix:
            base_score = 120
            matched = True
        
        # 2. 精确匹配"地级市+区县"形式
        elif query_no_suffix == adm2_no_suffix + city_name_no_suffix or \
             query_no_all_suffixes == adm2_no_suffix + city_name_no_suffix:
            base_score = 115
            matched = True
        
        # 3. 精确匹配"省+区县"形式
        elif query_no_suffix == adm1_no_suffix + city_name_no_suffix or \
             query_no_all_suffixes == adm1_no_suffix + city_name_no_suffix:
            base_score = 110
            matched = True
        
        # 4. 精确匹配城市名
        elif query == city_name or query_no_suffix == city_name_no_suffix:
            base_score = 100
            matched = True
        
        # 5. 查询去掉后缀后匹配城市名
        elif query_no_suffix == city_name_no_suffix:
            base_score = 95
            matched = True
        
        # 6. 查询以城市名结尾（如"北京昌平"以"昌平"结尾）
        elif len(city_name_no_suffix) >= 2 and query_no_suffix.endswith(city_name_no_suffix):
            prefix = query_no_suffix[:-len(city_name_no_suffix)]
            prefix_no_suffix = remove_all_suffixes(prefix)
            if prefix_no_suffix == adm2_no_suffix or prefix_no_suffix == adm1_no_suffix:
                base_score = 105
            elif prefix_no_suffix in adm2_no_suffix or adm2_no_suffix in prefix_no_suffix:
                base_score = 102
            elif prefix_no_suffix in adm1_no_suffix or adm1_no_suffix in prefix_no_suffix:
                base_score = 101
            else:
                base_score = 70 + len(city_name_no_suffix) * 3
            matched = True
        
        # 7. 查询包含城市名（且城市名长度>=2）
        elif len(city_name_no_suffix) >= 2 and city_name_no_suffix in query_no_suffix:
            base_score = 70 + len(city_name_no_suffix) * 3
            matched = True
        
        # 8. 城市名包含查询（且查询长度>=2）
        elif len(query_no_suffix) >= 2 and query_no_suffix in city_name_no_suffix:
            base_score = 65 + len(query_no_suffix) * 3
            matched = True
        
        # 9. "地级市+区县"部分匹配
        elif query_no_suffix in (adm2_no_suffix + city_name_no_suffix) or \
             (adm2_no_suffix + city_name_no_suffix) in query_no_suffix:
            base_score = 60
            matched = True
        
        # 10. "省+区县"部分匹配
        elif query_no_suffix in (adm1_no_suffix + city_name_no_suffix) or \
             (adm1_no_suffix + city_name_no_suffix) in query_no_suffix:
            base_score = 55
            matched = True
        
        if matched:
            # 额外加分：地级市优先（当有同名城市时）
            type_bonus = 5 if is_city_type(city) else 0
            results.append((base_score + type_bonus, city))
    
    # 按分数降序排序
    results.sort(key=lambda x: -x[0])
    return [city for _, city in results]


def search_online(keyword: str) -> list:
    """从和风天气 API 在线搜索"""
    try:
        import requests
        from dotenv import load_dotenv
        load_dotenv()
        
        API_KEY = os.getenv('API_KEY')
        API_DOMAIN = os.getenv('API_DOMAIN', 'nk7h2q8uut.re.qweatherapi.com')
        
        url = f'https://{API_DOMAIN}/geo/v2/city/lookup'
        params = {'location': keyword, 'key': API_KEY, 'number': 20}
        resp = requests.get(url, params=params, timeout=10)
        resp.encoding = 'utf-8'
        data = resp.json()
        
        if data.get('code') == '200':
            return [{
                'id': loc['id'],
                'name': loc.get('name', ''),
                'adm2': loc.get('adm2', ''),
                'adm1': loc.get('adm1', ''),
            } for loc in data.get('location', [])]
    except Exception as e:
        print(f"{YELLOW}在线搜索失败: {e}{RESET}")
    return []


def load_config_cities() -> dict:
    """从 config.py 加载当前城市列表"""
    if not CONFIG_PATH.exists():
        return {}
    
    with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 匹配 CITIES 字典
    match = re.search(r'CITIES\s*=\s*\{([^}]+)\}', content, re.DOTALL)
    if not match:
        return {}
    
    cities_str = match.group(1)
    cities = {}
    
    # 匹配每一行 'id': 'name'
    for line in cities_str.split('\n'):
        m = re.search(r"'(\d{9})'\s*:\s*'([^']+)'", line)
        if m:
            cities[m.group(1)] = m.group(2)
    
    return cities


def save_config_cities(cities: dict):
    """保存城市列表到 config.py"""
    if not CONFIG_PATH.exists():
        print(f"{RED}错误: 找不到 config.py{RESET}")
        return
    
    with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 构建新的 CITIES 字典
    cities_lines = []
    for city_id, city_name in cities.items():
        cities_lines.append(f"    '{city_id}': '{city_name}',")
    
    new_cities_str = "CITIES = {\n" + "\n".join(cities_lines) + "\n}"
    
    # 替换旧的 CITIES 字典
    pattern = r'CITIES\s*=\s*\{[^}]+\}'
    new_content = re.sub(pattern, new_cities_str, content, flags=re.DOTALL)
    
    # 更新注释中的城市数量
    count = len(cities)
    new_content = re.sub(
        r'# 城市配置（\d+ 个城市）',
        f'# 城市配置（{count} 个城市）',
        new_content
    )
    
    with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
        f.write(new_content)


def list_cities():
    """列出当前已添加的城市"""
    cities = load_config_cities()
    if not cities:
        print(f"{YELLOW}当前没有添加任何城市{RESET}")
        return
    
    print(f"\n{BOLD}{CYAN}当前已添加 {len(cities)} 个城市：{RESET}\n")
    print(f"  {'序号':<4} {'LocationID':<12} {'城市名称'}")
    print(f"  {'─'*4} {'─'*12} {'─'*10}")
    
    for i, (city_id, city_name) in enumerate(cities.items(), 1):
        print(f"  {i:<4} {city_id:<12} {city_name}")
    
    print()


def add_city():
    """添加城市"""
    cities_db = load_city_database()
    config_cities = load_config_cities()
    
    print(f"\n{BOLD}{CYAN}添加城市{RESET}")
    print(f"输入城市名称进行搜索（支持模糊匹配），输入 q 返回\n")
    
    while True:
        query = input(f"{GREEN}请输入城市名称 > {RESET}").strip()
        if query.lower() == 'q':
            break
        
        if not query:
            continue
        
        # 先从本地数据库搜索
        results = fuzzy_match(query, cities_db)
        
        # 如果本地没有结果，尝试在线搜索
        if not results:
            print(f"{YELLOW}本地未找到，正在在线搜索...{RESET}")
            results = search_online(query)
        
        if not results:
            print(f"{RED}未找到匹配的城市，请尝试其他关键词{RESET}\n")
            continue
        
        # 显示搜索结果
        print(f"\n{BOLD}找到 {len(results)} 个匹配结果：{RESET}\n")
        print(f"  {'序号':<4} {'LocationID':<12} {'省/市':<10} {'地级市':<10} {'区县'}")
        print(f"  {'─'*4} {'─'*12} {'─'*10} {'─'*10} {'─'*10}")
        
        # 最多显示 20 个结果
        display_results = results[:20]
        for i, city in enumerate(display_results, 1):
            # 检查是否已添加
            added = city['id'] in config_cities
            marker = f"{GREEN}✓{RESET}" if added else " "
            print(f"  {i:<4} {city['id']:<12} {city['adm1']:<10} {city['adm2']:<10} {city['name']} {marker}")
        
        if len(results) > 20:
            print(f"\n  {YELLOW}... 还有 {len(results) - 20} 个结果未显示{RESET}")
        
        print(f"\n  {CYAN}输入序号添加城市（多个用逗号分隔），按 Enter 跳过{RESET}")
        choice = input(f"  {GREEN}> {RESET}").strip()
        
        if choice:
            for idx in choice.split(','):
                idx = idx.strip()
                if idx.isdigit() and 1 <= int(idx) <= len(display_results):
                    city = display_results[int(idx) - 1]
                    if city['id'] in config_cities:
                        print(f"  {YELLOW}已存在: {city['name']}{RESET}")
                    else:
                        config_cities[city['id']] = city['name']
                        print(f"  {GREEN}已添加: {city['name']} ({city['id']}){RESET}")
                else:
                    print(f"  {RED}无效序号: {idx}{RESET}")
        
        print()
    
    # 保存到 config.py
    if config_cities != load_config_cities():
        save_config_cities(config_cities)
        print(f"{GREEN}已保存到 config.py{RESET}")


def remove_city():
    """删除城市"""
    config_cities = load_config_cities()
    
    if not config_cities:
        print(f"{YELLOW}当前没有添加任何城市{RESET}")
        return
    
    print(f"\n{BOLD}{CYAN}删除城市{RESET}")
    print(f"输入序号或城市名称进行删除，输入 q 返回\n")
    
    while True:
        # 显示当前城市列表
        city_list = list(config_cities.items())
        for i, (city_id, city_name) in enumerate(city_list, 1):
            print(f"  {i:<4} {city_id:<12} {city_name}")
        
        print(f"\n{CYAN}输入序号删除（多个用逗号分隔），或输入城市名称搜索{RESET}")
        choice = input(f"{GREEN}> {RESET}").strip()
        
        if choice.lower() == 'q':
            break
        
        if not choice:
            continue
        
        # 如果是数字，直接删除
        if choice.replace(',', '').isdigit():
            removed = []
            for idx in choice.split(','):
                idx = idx.strip()
                if idx.isdigit() and 1 <= int(idx) <= len(city_list):
                    city_id, city_name = city_list[int(idx) - 1]
                    del config_cities[city_id]
                    removed.append(city_name)
                    print(f"  {GREEN}已删除: {city_name}{RESET}")
                else:
                    print(f"  {RED}无效序号: {idx}{RESET}")
            
            if removed:
                save_config_cities(config_cities)
                print(f"\n{GREEN}已保存，删除了 {len(removed)} 个城市{RESET}")
        else:
            # 按名称搜索
            matches = [(cid, cname) for cid, cname in config_cities.items() 
                       if choice in cname or cname in choice]
            
            if not matches:
                print(f"{RED}未找到匹配的城市{RESET}\n")
                continue
            
            print(f"\n找到 {len(matches)} 个匹配：")
            for i, (city_id, city_name) in enumerate(matches, 1):
                print(f"  {i:<4} {city_id:<12} {city_name}")
            
            print(f"\n输入序号删除（多个用逗号分隔）")
            choice = input(f"{GREEN}> {RESET}").strip()
            
            if choice:
                removed = []
                for idx in choice.split(','):
                    idx = idx.strip()
                    if idx.isdigit() and 1 <= int(idx) <= len(matches):
                        city_id, city_name = matches[int(idx) - 1]
                        if city_id in config_cities:
                            del config_cities[city_id]
                            removed.append(city_name)
                            print(f"  {GREEN}已删除: {city_name}{RESET}")
                
                if removed:
                    save_config_cities(config_cities)
                    print(f"\n{GREEN}已保存，删除了 {len(removed)} 个城市{RESET}")
        
        print()


def main():
    """主函数"""
    print(f"\n{BOLD}{CYAN}{'='*50}{RESET}")
    print(f"{BOLD}{CYAN}  天气预报图片 - 城市管理工具{RESET}")
    print(f"{BOLD}{CYAN}{'='*50}{RESET}\n")
    
    while True:
        print(f"{BOLD}功能菜单：{RESET}")
        print(f"  {CYAN}1{RESET} - 查看当前城市列表")
        print(f"  {CYAN}2{RESET} - 添加城市")
        print(f"  {CYAN}3{RESET} - 删除城市")
        print(f"  {CYAN}q{RESET} - 退出")
        
        choice = input(f"\n{GREEN}请选择功能 > {RESET}").strip()
        
        if choice == '1':
            list_cities()
        elif choice == '2':
            add_city()
        elif choice == '3':
            remove_city()
        elif choice.lower() == 'q':
            print(f"\n{GREEN}再见！{RESET}\n")
            break
        else:
            print(f"{RED}无效选择，请重新输入{RESET}\n")


if __name__ == '__main__':
    main()
