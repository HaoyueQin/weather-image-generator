"""
获取和风天气全国城市LocationID（完整版v2）
直接遍历全国所有区县，不依赖层级关系

输出：
- CITY_IDS.md  按省份分组的参考表
- city_ids.csv 完整列表

用法：python get_city_ids_v2.py
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


def api_lookup(keyword: str, number: int = 20, adm: str = None) -> list:
    """调用和风天气GeoAPI搜索城市"""
    url = f'https://{API_DOMAIN}/geo/v2/city/lookup'
    params = {'location': keyword, 'key': API_KEY, 'number': number}
    if adm:
        params['adm'] = adm
    try:
        resp = requests.get(url, params=params, timeout=15)
        resp.encoding = 'utf-8'
        data = resp.json()
        if data.get('code') == '200':
            return data.get('location', [])
    except Exception as e:
        print(f"    请求失败: {e}")
    return []


def collect_all() -> list:
    """收集全国所有城市数据"""
    seen_ids = set()
    all_cities = []

    # 方法1：遍历省份
    provinces = [
        '北京', '天津', '上海', '重庆',
        '河北', '山西', '辽宁', '吉林', '黑龙江',
        '江苏', '浙江', '安徽', '福建', '江西', '山东',
        '河南', '湖北', '湖南', '广东', '海南',
        '四川', '贵州', '云南', '陕西', '甘肃', '青海',
        '台湾', '内蒙古', '广西', '西藏', '宁夏', '新疆',
        '香港', '澳门'
    ]

    print("=== 第一步：按省份搜索 ===")
    for province in provinces:
        print(f"【{province}】", end='', flush=True)
        locations = api_lookup(province, number=20)
        for loc in locations:
            if loc['id'] not in seen_ids:
                seen_ids.add(loc['id'])
                all_cities.append(loc)
        print(f" +{len(locations)}", flush=True)
        time.sleep(0.3)

    # 方法2：遍历常见城市名（补充遗漏）
    common_cities = [
        '呼和浩特', '包头', '鄂尔多斯', '赤峰', '通辽', '乌兰察布', '巴彦淖尔', '乌海',
        '银川', '石嘴山', '吴忠', '固原', '中卫',
        '西宁', '海东', '海北', '海南州', '果洛', '玉树', '海西',
        '拉萨', '日喀则', '昌都', '林芝', '山南', '那曲',
        '乌鲁木齐', '克拉玛依', '吐鲁番', '哈密', '喀什', '阿克苏',
        '库尔勒', '伊宁', '阿勒泰', '塔城', '石河子',
        '南宁', '柳州', '桂林', '梧州', '北海', '玉林', '百色', '河池', '钦州',
        '贵阳', '遵义', '六盘水', '安顺', '毕节', '铜仁',
        '昆明', '曲靖', '玉溪', '保山', '昭通', '丽江', '普洱', '临沧',
        '大理', '红河', '文山', '楚雄', '西双版纳', '德宏',
        '海口', '三亚', '三沙', '儋州',
        '太原', '大同', '阳泉', '长治', '晋城', '朔州', '晋中', '运城', '忻州', '临汾', '吕梁',
        '石家庄', '唐山', '秦皇岛', '邯郸', '邢台', '保定', '张家口', '承德', '沧州', '廊坊', '衡水',
        '沈阳', '大连', '鞍山', '抚顺', '本溪', '丹东', '锦州', '营口', '阜新', '辽阳', '盘锦', '铁岭', '朝阳', '葫芦岛',
        '长春', '吉林', '四平', '辽源', '通化', '白山', '松原', '白城',
        '哈尔滨', '齐齐哈尔', '鸡西', '鹤岗', '双鸭山', '大庆', '伊春', '佳木斯', '七台河', '牡丹江', '黑河', '绥化',
        '南京', '无锡', '徐州', '常州', '苏州', '南通', '连云港', '淮安', '盐城', '扬州', '镇江', '泰州', '宿迁',
        '杭州', '宁波', '温州', '嘉兴', '湖州', '绍兴', '金华', '衢州', '舟山', '台州', '丽水',
        '合肥', '芜湖', '蚌埠', '淮南', '马鞍山', '淮北', '铜陵', '安庆', '黄山', '滁州', '阜阳', '宿州', '六安', '亳州', '池州', '宣城',
        '福州', '厦门', '莆田', '三明', '泉州', '漳州', '南平', '龙岩', '宁德',
        '南昌', '景德镇', '萍乡', '九江', '新余', '鹰潭', '赣州', '吉安', '宜春', '抚州', '上饶',
        '济南', '青岛', '淄博', '枣庄', '东营', '烟台', '潍坊', '济宁', '泰安', '威海', '日照', '临沂', '德州', '聊城', '滨州', '菏泽',
        '郑州', '开封', '洛阳', '平顶山', '安阳', '鹤壁', '新乡', '焦作', '濮阳', '许昌', '漯河', '三门峡', '南阳', '商丘', '信阳', '周口', '驻马店',
        '武汉', '黄石', '十堰', '宜昌', '襄阳', '鄂州', '荆门', '孝感', '荆州', '黄冈', '咸宁', '随州',
        '长沙', '株洲', '湘潭', '衡阳', '邵阳', '岳阳', '常德', '张家界', '益阳', '郴州', '永州', '怀化', '娄底', '湘西',
        '广州', '韶关', '深圳', '珠海', '汕头', '佛山', '江门', '湛江', '茂名', '肇庆', '惠州', '梅州', '汕尾', '河源', '阳江', '清远', '东莞', '中山', '潮州', '揭阳', '云浮',
        '成都', '自贡', '攀枝花', '泸州', '德阳', '绵阳', '广元', '遂宁', '内江', '乐山', '南充', '眉山', '宜宾', '广安', '达州', '雅安', '巴中', '资阳', '阿坝', '甘孜', '凉山',
    ]

    print("\n=== 第二步：按城市名补充 ===")
    for city_name in common_cities:
        if any(c.get('name') == city_name and c.get('type') == 'city' for c in all_cities):
            continue  # 已存在

        print(f"  {city_name}...", end='', flush=True)
        locations = api_lookup(city_name, number=20)
        added = 0
        for loc in locations:
            if loc['id'] not in seen_ids:
                seen_ids.add(loc['id'])
                all_cities.append(loc)
                added += 1
        print(f" +{added}", flush=True)
        time.sleep(0.3)

    # 按省份和名称排序
    all_cities.sort(key=lambda x: (x.get('adm1', ''), x.get('adm2', ''), x.get('name', '')))
    return all_cities


def save_markdown(cities: list, filename: str = 'CITY_IDS.md'):
    """保存为Markdown"""
    with open(filename, 'w', encoding='utf-8') as f:
        f.write("# 和风天气城市 LocationID 完整参考表\n\n")
        f.write(f"共 **{len(cities)}** 个城市/区县\n\n")
        f.write("## 使用方法\n\n")
        f.write("在 `config.py` 的 `CITIES` 字典中添加城市：\n\n")
        f.write("```python\nCITIES = {\n    '101010100': '北京',\n    '101010200': '海淀',\n    # ...\n}\n```\n\n")

        # 按省份分组
        current_province = None
        for city in cities:
            province = city.get('adm1', '未知')
            if province != current_province:
                if current_province:
                    f.write("\n")
                current_province = province
                f.write(f"## {province}\n\n")
                f.write("| LocationID | 城市 | 区县 | 经度 | 纬度 |\n")
                f.write("|------------|------|------|------|------|\n")

            f.write(f"| {city['id']} | {city.get('adm2', '')} | {city.get('name', '')} | {city.get('lon', '')} | {city.get('lat', '')} |\n")

    print(f"已保存 Markdown 到 {filename}")


def save_csv(cities: list, filename: str = 'city_ids.csv'):
    """保存为CSV"""
    fieldnames = ['id', 'name', 'adm2', 'adm1', 'lat', 'lon']
    with open(filename, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(cities)
    print(f"已保存 CSV 到 {filename}（{len(cities)} 条）")


def save_json(cities: list, filename: str = 'city_ids.json'):
    """保存为JSON"""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(cities, f, ensure_ascii=False, indent=2)
    print(f"已保存 JSON 到 {filename}")


if __name__ == '__main__':
    print("=" * 50)
    print("  和风天气全国城市ID获取工具（完整版v2）")
    print("=" * 50)
    print()

    if not API_KEY:
        print("错误: 请在 .env 文件中配置 API_KEY")
        exit(1)

    cities = collect_all()

    print("\n" + "=" * 50)
    print(f"共获取 {len(cities)} 个城市/区县")
    print("=" * 50)
    print()

    save_markdown(cities)
    save_csv(cities)
    save_json(cities)

    # 统计各省份
    print("\n各省份统计:")
    province_stats = {}
    for city in cities:
        p = city.get('adm1', '未知')
        province_stats[p] = province_stats.get(p, 0) + 1
    for p in sorted(province_stats.keys()):
        print(f"  {p}: {province_stats[p]}")
