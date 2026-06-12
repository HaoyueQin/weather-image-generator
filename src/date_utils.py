"""
日期和节日工具模块

处理农历日期、节气、节日信息。
"""

from datetime import datetime, timedelta
from typing import List, Tuple, Optional, Dict


# 农历月份中文
LUNAR_MONTHS = ["", "正", "二", "三", "四", "五", "六", "七", "八", "九", "十", "冬", "腊"]

# 农历日期中文
LUNAR_DAYS = [
    "", "初一", "初二", "初三", "初四", "初五", "初六", "初七", "初八", "初九", "初十",
    "十一", "十二", "十三", "十四", "十五", "十六", "十七", "十八", "十九", "二十",
    "廿一", "廿二", "廿三", "廿四", "廿五", "廿六", "廿七", "廿八", "廿九", "三十",
]

# 天干
TIANGAN = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]

# 地支
DIZHI = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]

# 生肖
SHENGXIAO = ["鼠", "牛", "虎", "兔", "龙", "蛇", "马", "羊", "猴", "鸡", "狗", "猪"]

# 星期
WEEKDAYS = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]

# 二十四节气
SOLAR_TERMS = [
    "小寒", "大寒", "立春", "雨水", "惊蛰", "春分",
    "清明", "谷雨", "立夏", "小满", "芒种", "夏至",
    "小暑", "大暑", "立秋", "处暑", "白露", "秋分",
    "寒露", "霜降", "立冬", "小雪", "大雪", "冬至",
]

# 二十四节气日期（近似值，每年略有变化）
SOLAR_TERMS_DATES_2025 = {
    "小寒": (1, 5), "大寒": (1, 20), "立春": (2, 3), "雨水": (2, 18),
    "惊蛰": (3, 5), "春分": (3, 20), "清明": (4, 4), "谷雨": (4, 19),
    "立夏": (5, 5), "小满": (5, 20), "芒种": (6, 5), "夏至": (6, 21),
    "小暑": (7, 6), "大暑": (7, 22), "立秋": (8, 7), "处暑": (8, 22),
    "白露": (9, 7), "秋分": (9, 22), "寒露": (10, 8), "霜降": (10, 23),
    "立冬": (11, 7), "小雪": (11, 22), "大雪": (12, 6), "冬至": (12, 21),
}

SOLAR_TERMS_DATES_2026 = {
    "小寒": (1, 5), "大寒": (1, 20), "立春": (2, 4), "雨水": (2, 18),
    "惊蛰": (3, 5), "春分": (3, 20), "清明": (4, 4), "谷雨": (4, 20),
    "立夏": (5, 5), "小满": (5, 21), "芒种": (6, 5), "夏至": (6, 21),
    "小暑": (7, 7), "大暑": (7, 22), "立秋": (8, 7), "处暑": (8, 23),
    "白露": (9, 7), "秋分": (9, 23), "寒露": (10, 8), "霜降": (10, 23),
    "立冬": (11, 7), "小雪": (11, 22), "大雪": (12, 7), "冬至": (12, 21),
}

# 常见节日
FESTIVALS = {
    # 公历节日
    (1, 1): "元旦",
    (2, 14): "情人节",
    (3, 8): "妇女节",
    (3, 12): "植树节",
    (4, 1): "愚人节",
    (5, 1): "劳动节",
    (5, 4): "青年节",
    (6, 1): "儿童节",
    (7, 1): "建党节",
    (8, 1): "建军节",
    (9, 10): "教师节",
    (10, 1): "国庆节",
    (12, 25): "圣诞节",
    # 农历节日（需要特殊处理）
    # 正月初一: 春节
    # 正月十五: 元宵节
    # 五月初五: 端午节
    # 七月初七: 七夕
    # 七月十五: 中元节
    # 八月十五: 中秋节
    # 九月初九: 重阳节
    # 腊月三十: 除夕
}

# 农历节日
LUNAR_FESTIVALS = {
    (1, 1): "春节",
    (1, 15): "元宵节",
    (5, 5): "端午节",
    (7, 7): "七夕",
    (7, 15): "中元节",
    (8, 15): "中秋节",
    (9, 9): "重阳节",
    (12, 30): "除夕",
}


def get_cyclical_date(year: int, month: int, day: int) -> str:
    """
    获取天干地支年

    Args:
        year: 公历年份

    Returns:
        天干地支年字符串
    """
    tiangan_idx = (year - 4) % 10
    dizhi_idx = (year - 4) % 12
    return f"{TIANGAN[tiangan_idx]}{DIZHI[dizhi_idx]}"


def get_shengxiao(year: int) -> str:
    """
    获取生肖

    Args:
        year: 公历年份

    Returns:
        生肖字符串
    """
    return SHENGXIAO[(year - 4) % 12]


def get_solar_term(year: int, month: int, day: int) -> Optional[str]:
    """
    获取当天的节气

    Args:
        year: 公历年份
        month: 公历月份
        day: 公历日期

    Returns:
        节气名称，如果当天不是节气则返回None
    """
    # 选择对应年份的节气表
    if year == 2025:
        solar_terms = SOLAR_TERMS_DATES_2025
    elif year == 2026:
        solar_terms = SOLAR_TERMS_DATES_2026
    else:
        # 简单估算
        solar_terms = SOLAR_TERMS_DATES_2026

    for term_name, (m, d) in solar_terms.items():
        if m == month and d == day:
            return term_name
    return None


def get_festival(month: int, day: int) -> Optional[str]:
    """
    获取公历节日

    Args:
        month: 公历月份
        day: 公历日期

    Returns:
        节日名称
    """
    return FESTIVALS.get((month, day))


def get_upcoming_events(
    target_date: datetime, num_events: int = 5
) -> List[Tuple[datetime, str]]:
    """
    获取即将到来的节日和节气

    Args:
        target_date: 起始日期
        num_events: 返回事件数量

    Returns:
        [(日期, 事件名称), ...]
    """
    events = []
    year = target_date.year

    # 收集当年所有节气
    if year == 2025:
        solar_terms = SOLAR_TERMS_DATES_2025
    elif year == 2026:
        solar_terms = SOLAR_TERMS_DATES_2026
    else:
        solar_terms = SOLAR_TERMS_DATES_2026

    for term_name, (m, d) in solar_terms.items():
        try:
            event_date = datetime(year, m, d)
            if event_date > target_date:
                events.append((event_date, term_name))
        except ValueError:
            pass

    # 收集公历节日
    for (m, d), name in FESTIVALS.items():
        try:
            event_date = datetime(year, m, d)
            if event_date > target_date:
                events.append((event_date, name))
        except ValueError:
            pass

    # 按日期排序
    events.sort(key=lambda x: x[0])

    return events[:num_events]


def format_date_info(date: datetime) -> Dict[str, str]:
    """
    格式化日期信息

    Args:
        date: 日期

    Returns:
        日期信息字典
    """
    cyclical = get_cyclical_date(date.year, date.month, date.day)
    shengxiao = get_shengxiao(date.year)
    weekday = WEEKDAYS[date.weekday()]
    solar_term = get_solar_term(date.year, date.month, date.day)
    festival = get_festival(date.month, date.day)

    return {
        "solar_date": date.strftime("%Y年%m月%d日"),
        "weekday": weekday,
        "cyclical_year": f"{cyclical}{shengxiao}年",
        "solar_term": solar_term,
        "festival": festival,
    }
