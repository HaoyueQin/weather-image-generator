"""
日期和节日工具模块

处理农历日期、节气、节日信息。
节气计算使用 sxtwl 库（基于寿星天文历算法，精度高）。
"""

import sxtwl
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

# 节气名称（sxtwl 使用的索引顺序：0=冬至, 1=小寒, 2=大寒, 3=立春, ...23=大雪）
JIEQI_NAMES = [
    "冬至", "小寒", "大寒", "立春", "雨水", "惊蛰", "春分",
    "清明", "谷雨", "立夏", "小满", "芒种", "夏至",
    "小暑", "大暑", "立秋", "处暑", "白露", "秋分",
    "寒露", "霜降", "立冬", "小雪", "大雪",
]

# 公历节日
FESTIVALS = {
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
    """获取天干地支年"""
    day_info = sxtwl.fromSolar(year, month, day)
    yTG = day_info.getYearGZ()
    return f"{TIANGAN[yTG.tg]}{DIZHI[yTG.dz]}"


def get_shengxiao(year: int) -> str:
    """获取生肖"""
    return SHENGXIAO[(year - 4) % 12]


def get_solar_term(year: int, month: int, day: int) -> Optional[str]:
    """
    获取当天的节气

    Args:
        year: 公历年份
        month: 公历月份
        day: 公历日期

    Returns:
        节气名称，如果当天不是节气则返回 None
    """
    day_info = sxtwl.fromSolar(year, month, day)
    if day_info.hasJieQi():
        jq_idx = day_info.getJieQi()
        if 0 <= jq_idx < len(JIEQI_NAMES):
            return JIEQI_NAMES[jq_idx]
    return None


def get_festival(month: int, day: int) -> Optional[str]:
    """获取公历节日"""
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

    # 用 getJieQiByYear 高效获取当年及下一年的节气
    for y in (year, year + 1):
        jieqi_list = sxtwl.getJieQiByYear(y)
        for item in jieqi_list:
            t = sxtwl.JD2DD(item.jd)
            event_date = datetime(int(t.Y), int(t.M), int(t.D))
            if event_date > target_date and 0 <= item.jqIndex < len(JIEQI_NAMES):
                events.append((event_date, JIEQI_NAMES[item.jqIndex]))

    # 如果节气不够，再补充公历节日
    if len(events) < num_events:
        for (m, d), name in FESTIVALS.items():
            try:
                event_date = datetime(year, m, d)
                if event_date > target_date:
                    events.append((event_date, name))
            except ValueError:
                pass

    # 按日期排序，取前 N 个
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
    # 用 sxtwl 获取农历信息
    day_info = sxtwl.fromSolar(date.year, date.month, date.day)

    cyclical = get_cyclical_date(date.year, date.month, date.day)
    shengxiao = get_shengxiao(date.year)
    weekday = WEEKDAYS[date.weekday()]
    solar_term = get_solar_term(date.year, date.month, date.day)
    festival = get_festival(date.month, date.day)

    # 农历信息
    lunar_month = day_info.getLunarMonth()
    lunar_day = day_info.getLunarDay()
    is_leap = day_info.isLunarLeap()
    lunar_month_str = ("闰" if is_leap else "") + LUNAR_MONTHS[lunar_month]
    lunar_day_str = LUNAR_DAYS[lunar_day]

    return {
        "solar_date": date.strftime("%Y年%m月%d日"),
        "weekday": weekday,
        "cyclical_year": f"{cyclical}{shengxiao}年",
        "lunar_date": f"农历{LUNAR_MONTHS[day_info.getLunarMonth()]}月{lunar_day_str}",
        "solar_term": solar_term,
        "festival": festival,
    }
