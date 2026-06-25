"""
天气图片生成模块 - 高级感版 v3

修复：emoji渲染、字体粗细、卡片装饰、预警布局
"""

from PIL import Image, ImageDraw, ImageFont, ImageFilter
from typing import Dict, List, Tuple, Any
from datetime import datetime
import os
import re

# 天气符号映射（使用 Unicode 符号而非 emoji，兼容性更好）
WEATHER_SYMBOL = {
    "晴": "\u2600",      # ☀
    "多云": "\u26C5",    # ⛅
    "阴": "\u2601",      # ☁
    "小雨": "\u2602",    # ☂
    "中雨": "\u2614",    # ☔
    "大雨": "\u2614",    # ☔
    "暴雨": "\u26C8",    # ⛈
    "雷阵雨": "\u26C8",  # ⛈
    "阵雨": "\u2602",    # ☂
    "毛毛雨": "\u2602",  # ☂
    "小雪": "\u2744",    # ❄
    "中雪": "\u2744",    # ❄
    "大雪": "\u2744",    # ❄
    "暴雪": "\u2744",    # ❄
    "雨夹雪": "\u2603",  # ☃
    "冻雨": "\u2603",    # ☃
    "雾": "\u2603",      # ☃ (foggy)
    "霾": "\u2601",      # ☁
    "沙尘暴": "\u2601",  # ☁
    "晴转多云": "\u26C5", # ⛅
    "多云转晴": "\u26C5", # ⛅
}


def get_weather_symbol(text: str) -> str:
    """根据天气描述返回对应 Unicode 符号"""
    if not text:
        return "\u2600"
    for key, sym in WEATHER_SYMBOL.items():
        if key in text:
            return sym
    return "\u2600"


def parse_warning_title(title: str) -> str:
    """
    解析预警标题，只提取"发布"后面的预警内容
    例如："北京市气象台发布暴雨黄色预警信号" -> "暴雨黄色预警"
    """
    if not title:
        return ""
    match = re.search(r'发布(.+预警)', title)
    return match.group(1) if match else ""


# 字体路径常量
FONT_DIR = r"C:\Windows\Fonts"
FONT_MSYH = os.path.join(FONT_DIR, "msyh.ttc")
FONT_MSYHBD = os.path.join(FONT_DIR, "msyhbd.ttc")
FONT_KAI = os.path.join(FONT_DIR, "simkai.ttf")
FONT_STKAITI = os.path.join(FONT_DIR, "STKAITI.TTF")
FONT_FZSTK = os.path.join(FONT_DIR, "FZSTK.TTF")
FONT_XINGKAI = os.path.join(FONT_DIR, "STXINGKA.TTF")  # 华文行楷
FONT_ENG = os.path.join(FONT_DIR, "Georgia.ttf")
FONT_ENG_SANS = os.path.join(FONT_DIR, "calibri.ttf")
FONT_EMOJI = os.path.join(FONT_DIR, "seguiemj.ttf")


class WeatherImageGenerator:

    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.width = self.config.get("width", 1440)
        self.colors = self.config.get("colors", {})
        self._fonts = {}

    # ── 字体系统 ──────────────────────────────────────────

    def _get_font(self, size: int, style: str = "default") -> ImageFont.FreeTypeFont:
        key = (size, style)
        if key not in self._fonts:
            try:
                if style == "title":
                    # 行楷：优先华文行楷，备选方正舒体
                    path = FONT_XINGKAI if os.path.exists(FONT_XINGKAI) else FONT_FZSTK
                    self._fonts[key] = ImageFont.truetype(path, size)
                elif style == "kai":
                    self._fonts[key] = ImageFont.truetype(FONT_KAI, size)
                elif style == "kai_bold":
                    # 华文楷体（比 simkai 更粗）
                    path = FONT_STKAITI if os.path.exists(FONT_STKAITI) else FONT_KAI
                    self._fonts[key] = ImageFont.truetype(path, size)
                elif style == "eng":
                    self._fonts[key] = ImageFont.truetype(FONT_ENG, size)
                elif style == "eng_sans":
                    self._fonts[key] = ImageFont.truetype(FONT_ENG_SANS, size)
                elif style == "bold":
                    self._fonts[key] = ImageFont.truetype(FONT_MSYHBD, size)
                elif style == "emoji":
                    self._fonts[key] = ImageFont.truetype(FONT_EMOJI, size)
                else:
                    self._fonts[key] = ImageFont.truetype(FONT_MSYH, size, index=0)
            except Exception:
                self._fonts[key] = ImageFont.load_default()
        return self._fonts[key]

    # ── 绘图工具 ──────────────────────────────────────────

    def _rr(self, draw, xy, r, fill=None, outline=None, width=1):
        draw.rounded_rectangle(xy, radius=r, fill=fill, outline=outline, width=width)

    def _draw_gradient_bg(self, img: Image.Image):
        """三段渐变背景：浅紫 → 浅蓝 → 浅绿"""
        w, h = img.size
        top = self.colors.get("bg_top", (235, 230, 250))
        mid = self.colors.get("bg_mid", (225, 240, 255))
        bot = self.colors.get("bg_bottom", (225, 250, 240))
        pixels = img.load()
        for y in range(h):
            ratio = y / max(h - 1, 1)
            if ratio < 0.5:
                r2 = ratio * 2
                r = int(top[0] + (mid[0] - top[0]) * r2)
                g = int(top[1] + (mid[1] - top[1]) * r2)
                b = int(top[2] + (mid[2] - top[2]) * r2)
            else:
                r2 = (ratio - 0.5) * 2
                r = int(mid[0] + (bot[0] - mid[0]) * r2)
                g = int(mid[1] + (bot[1] - mid[1]) * r2)
                b = int(mid[2] + (bot[2] - mid[2]) * r2)
            for x in range(w):
                pixels[x, y] = (r, g, b)

    def _draw_decorations(self, img: Image.Image, y_cities_start: int,
                          y_cities_end: int, y_footer: int):
        """绘制装饰花纹：全局分布"""
        draw = ImageDraw.Draw(img, 'RGBA')
        w = self.width
        c_purple = self.colors.get("deco_purple", (180, 160, 220))
        c_blue = self.colors.get("deco_blue", (140, 190, 240))
        c_green = self.colors.get("deco_green", (140, 210, 190))

        # 顶部渐变装饰条
        bar_h = 6
        seg = w // 3
        for x in range(seg):
            ratio = x / seg
            r = int(c_purple[0] + (c_blue[0] - c_purple[0]) * ratio)
            g = int(c_purple[1] + (c_blue[1] - c_purple[1]) * ratio)
            b = int(c_purple[2] + (c_blue[2] - c_purple[2]) * ratio)
            draw.line([(x, 0), (x, bar_h - 1)], fill=(r, g, b, 200))
        for x in range(seg, seg * 2):
            ratio = (x - seg) / seg
            r = int(c_blue[0] + (c_green[0] - c_blue[0]) * ratio)
            g = int(c_blue[1] + (c_green[1] - c_blue[1]) * ratio)
            b = int(c_blue[2] + (c_green[2] - c_blue[2]) * ratio)
            draw.line([(x, 0), (x, bar_h - 1)], fill=(r, g, b, 200))
        for x in range(seg * 2, w):
            draw.line([(x, 0), (x, bar_h - 1)], fill=(*c_green, 200))

        # 右上角装饰圆环
        for cx, cy, radius, color in [
            (w - 120, 100, 80, c_purple), (w - 60, 160, 50, c_blue),
            (w - 180, 50, 35, c_green),
        ]:
            draw.ellipse((cx - radius, cy - radius, cx + radius, cy + radius),
                         outline=(*color, 30), width=2)
            draw.ellipse((cx - radius + 6, cy - radius + 6, cx + radius - 6, cy + radius - 6),
                         outline=(*color, 18), width=1)

        # 中间区域装饰
        mid_y = (y_cities_start + y_cities_end) // 2
        for cx, cy, radius, color in [
            (30, mid_y - 100, 45, c_purple), (45, mid_y + 80, 30, c_blue),
            (25, mid_y + 200, 55, c_green),
            (w - 30, mid_y - 50, 40, c_green), (w - 45, mid_y + 120, 35, c_purple),
            (w - 25, mid_y - 180, 50, c_blue),
        ]:
            draw.ellipse((cx - radius, cy - radius, cx + radius, cy + radius),
                         outline=(*color, 22), width=2)

        # 底部圆环
        for cx, cy, radius, color in [
            (100, y_footer - 80, 60, c_green), (160, y_footer - 30, 40, c_blue),
            (w - 100, y_footer - 60, 50, c_purple),
        ]:
            draw.ellipse((cx - radius, cy - radius, cx + radius, cy + radius),
                         outline=(*color, 20), width=2)

        # 散落圆点
        dots = [
            (200, 45, 4, c_purple), (400, 35, 3, c_blue), (650, 50, 4, c_green),
            (900, 40, 3, c_purple), (1100, 55, 4, c_blue), (1300, 42, 3, c_green),
            (80, mid_y - 60, 3, c_purple), (80, mid_y + 40, 4, c_blue),
            (w - 80, mid_y - 30, 3, c_green), (w - 80, mid_y + 70, 4, c_purple),
            (150, y_footer - 50, 3, c_purple), (350, y_footer - 40, 4, c_blue),
            (600, y_footer - 55, 3, c_green), (850, y_footer - 35, 4, c_purple),
            (1100, y_footer - 48, 3, c_blue), (1300, y_footer - 38, 4, c_green),
        ]
        for dx, dy, dr, dc in dots:
            draw.ellipse((dx - dr, dy - dr, dx + dr, dy + dr), fill=(*dc, 40))

        # 十字星
        for cx, cy, color in [
            (120, mid_y - 150, c_purple), (w - 120, mid_y + 150, c_green),
            (200, mid_y + 100, c_blue), (w - 200, mid_y - 100, c_purple),
        ]:
            s = 6
            draw.line([(cx - s, cy), (cx + s, cy)], fill=(*color, 35), width=1)
            draw.line([(cx, cy - s), (cx, cy + s)], fill=(*color, 35), width=1)

    def _draw_card_inner_decoration(self, draw, cx, cy, card_w, card_h, pad, idx):
        """城市卡片内部装饰：左上角小装饰点"""
        c_purple = self.colors.get("deco_purple", (180, 160, 220))
        c_blue = self.colors.get("deco_blue", (140, 190, 240))
        c_green = self.colors.get("deco_green", (140, 210, 190))
        colors = [c_purple, c_blue, c_green]
        color = colors[idx % 3]

        # 左上角：小装饰点
        draw.ellipse((cx + pad - 5, cy + pad - 5, cx + pad + 3, cy + pad + 3),
                     fill=(*color, 25))

    def _draw_glass_cards_batch(self, img: Image.Image, cards: List[Tuple[int, int, int, int]],
                                 radius: int = 20, opacity: int = 150, shadow_offset: int = 8):
        """批量绘制玻璃卡片"""
        if not cards:
            return
        c_shadow = self.colors.get("card_shadow", (170, 180, 210))

        shadow = Image.new("RGBA", img.size, (0, 0, 0, 0))
        sd = ImageDraw.Draw(shadow)
        for (x1, y1, x2, y2) in cards:
            sd.rounded_rectangle(
                (x1 + shadow_offset, y1 + shadow_offset, x2 + shadow_offset, y2 + shadow_offset),
                radius=radius, fill=(*c_shadow, 45)
            )
        shadow = shadow.filter(ImageFilter.GaussianBlur(radius=shadow_offset * 2))
        img.paste(Image.alpha_composite(img.convert("RGBA"), shadow).convert("RGB"), (0, 0))

        for (x1, y1, x2, y2) in cards:
            region = img.crop((x1, y1, x2, y2)).filter(ImageFilter.GaussianBlur(radius=18))
            overlay = Image.new("RGBA", region.size, (255, 255, 255, opacity))
            glass = Image.alpha_composite(region.convert("RGBA"), overlay)
            mask = Image.new("L", region.size, 0)
            ImageDraw.Draw(mask).rounded_rectangle((0, 0, region.size[0], region.size[1]),
                                                    radius=radius, fill=255)
            img.paste(glass.convert("RGB"), (x1, y1), mask)
            draw = ImageDraw.Draw(img, 'RGBA')
            draw.rounded_rectangle((x1, y1, x2, y2), radius=radius,
                                   outline=(255, 255, 255, 160), width=2)

    def _draw_gradient_line(self, draw, x1, y, x2, color_start, color_end, width=2):
        """绘制渐变水平线"""
        segs = max(x2 - x1, 1)
        for i in range(segs):
            ratio = i / segs
            r = int(color_start[0] + (color_end[0] - color_start[0]) * ratio)
            g = int(color_start[1] + (color_end[1] - color_start[1]) * ratio)
            b = int(color_start[2] + (color_end[2] - color_start[2]) * ratio)
            draw.line([(x1 + i, y), (x1 + i, y + width - 1)], fill=(r, g, b))

    # ── 主入口 ────────────────────────────────────────────

    def generate_image(self, date_info, cities_weather, upcoming_events, output_path):
        try:
            num = len(cities_weather)
            card_h = 270
            card_gap = 16
            rows = (num + 1) // 2
            margin = 60

            total_h = margin + 170 + 240 + 55 + rows * (card_h + card_gap) + 50 + 80
            img = Image.new("RGBA", (self.width, total_h), (255, 255, 255, 255))
            self._draw_gradient_bg(img)

            # 花纹层：在背景渐变之上、内容之前绘制
            y_after_header_est = margin + 170
            y_after_events_est = y_after_header_est + 240
            y_cities_start_est = y_after_events_est + 55
            y_cities_end_est = y_cities_start_est + rows * (card_h + card_gap)
            y_footer_est = y_cities_end_est + 10 + 50
            self._draw_decorations(img, y_cities_start_est, y_cities_end_est, y_footer_est)

            y = margin
            y = self._draw_header(img, date_info, y)
            y = self._draw_events(img, upcoming_events, y)
            y_cities_start = y + 55
            y_cities_end = y_cities_start + rows * (card_h + card_gap)
            y = self._draw_cities(img, cities_weather, y, card_h, card_gap)
            y_footer = y
            y = self._draw_footer(img, y)

            img = img.crop((0, 0, self.width, min(y + margin, total_h)))
            img = img.convert("RGB")
            os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
            img.save(output_path, quality=95)
            return True
        except Exception as e:
            print(f"Error: {e}")
            import traceback; traceback.print_exc()
            return False

    # ── Header ────────────────────────────────────────────

    def _draw_header(self, img: Image.Image, date_info, y):
        draw = ImageDraw.Draw(img, 'RGBA')
        c_title = self.colors.get("title", (50, 40, 100))
        c_primary = self.colors.get("text_primary", (35, 40, 65))
        c_secondary = self.colors.get("text_secondary", (110, 120, 150))
        c_tertiary = self.colors.get("text_tertiary", (155, 165, 190))
        c_deco_purple = self.colors.get("deco_purple", (180, 160, 220))
        c_deco_green = self.colors.get("deco_green", (140, 210, 190))
        mx = 60

        # 标题（华文行楷，统一浅蓝色）
        f_title = self._get_font(92, "title")
        c_light_blue = (100, 160, 230)
        draw.text((mx, y + 5), "天气预报", font=f_title, fill=c_light_blue)

        # 英文副标题（Georgia 衬线体，放在标题右上角）
        f_subtitle = self._get_font(28, "eng")
        title_w = draw.textlength("天气预报", font=f_title)
        draw.text((mx + title_w + 15, y + 13), "WEATHER FORECAST", font=f_subtitle, fill=c_tertiary)

        # 右侧日期
        sx = self.width - mx
        f_date = self._get_font(44)
        date_text = f"{date_info['solar_date']}  {date_info['weekday']}"
        draw.text((sx, y + 10), date_text, font=f_date, fill=c_primary, anchor="ra")

        # 农历 + 年份
        f_small = self._get_font(28)
        lunar = date_info.get('lunar_date', '')
        cyclical = date_info.get('cyclical_year', '')
        info_text = f"{lunar}  {cyclical}"
        draw.text((sx, y + 62), info_text, font=f_small, fill=c_secondary, anchor="ra")

        # 节气标签
        st = date_info.get('solar_term')
        if st:
            f_term = self._get_font(26)
            tw = draw.textlength(st, font=f_term) + 20
            self._rr(draw, (mx, y + 95, mx + tw + 10, y + 123), 12,
                     fill=(218, 245, 228))
            draw.text((mx + 10, y + 97), st, font=f_term,
                      fill=self.colors.get("success", (60, 175, 120)))

        # 渐变分割线
        y_line = y + 140
        self._draw_gradient_line(draw, mx, y_line, self.width - mx,
                                 c_deco_purple, c_deco_green, width=3)

        return y_line + 25

    # ── Events ────────────────────────────────────────────

    def _draw_events(self, img: Image.Image, events, y):
        if not events:
            return y

        draw = ImageDraw.Draw(img, 'RGBA')
        mx = 60
        section_h = 230

        # 毛玻璃卡片
        x1, y1, x2, y2 = mx, y, self.width - mx, y + section_h
        c_shadow = self.colors.get("card_shadow", (170, 180, 210))
        shadow = Image.new("RGBA", img.size, (0, 0, 0, 0))
        ImageDraw.Draw(shadow).rounded_rectangle((x1 + 8, y1 + 8, x2 + 8, y2 + 8), radius=20, fill=(*c_shadow, 45))
        shadow = shadow.filter(ImageFilter.GaussianBlur(radius=16))
        img.paste(Image.alpha_composite(img.convert("RGBA"), shadow).convert("RGB"), (0, 0))
        region = img.crop((x1, y1, x2, y2)).filter(ImageFilter.GaussianBlur(radius=18))
        overlay = Image.new("RGBA", region.size, (255, 255, 255, 100))
        glass = Image.alpha_composite(region.convert("RGBA"), overlay)
        mask = Image.new("L", region.size, 0)
        ImageDraw.Draw(mask).rounded_rectangle((0, 0, region.size[0], region.size[1]), radius=20, fill=255)
        img.paste(glass.convert("RGB"), (x1, y1), mask)
        draw = ImageDraw.Draw(img, 'RGBA')
        draw.rounded_rectangle((x1, y1, x2, y2), radius=20, outline=(255, 255, 255, 160), width=2)

        c_accent = self.colors.get("text_accent", (100, 130, 220))
        c_deco_purple = self.colors.get("deco_purple", (180, 160, 220))

        # 标题（楷体）
        f_title = self._get_font(36, "kai")
        draw.text((mx + 28, y + 16), "即将到来", font=f_title, fill=c_accent)
        draw.rounded_rectangle((mx + 28, y + 58, mx + 80, y + 62), radius=2, fill=(*c_deco_purple, 120))

        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        num = min(len(events), 5)
        f_name = self._get_font(32)
        f_count = self._get_font(52, "bold")
        f_unit = self._get_font(26)
        f_date = self._get_font(24)

        c_primary = self.colors.get("text_primary", (35, 40, 65))
        c_secondary = self.colors.get("text_secondary", (110, 120, 150))
        c_divider = self.colors.get("divider", (210, 215, 235))

        content_w = self.width - mx * 2 - 60
        item_w = content_w // num
        start_x = mx + 30

        for i, (ed, en) in enumerate(events[:5]):
            dl = (ed - today).days
            cd = f"{dl}" if dl > 0 else "今"
            unit = "天" if dl > 0 else ""
            dt = ed.strftime("%m/%d")
            uy = y + 75

            # 在等宽槽位内水平居中
            slot_x = start_x + i * item_w
            # 事件名居中
            en_w = draw.textlength(en, font=f_name)
            draw.text((slot_x + (item_w - en_w) // 2, uy), en, font=f_name, fill=c_primary)
            # 倒计天数居中（大字+单位一起居中）
            cd_w = draw.textlength(cd, font=f_count)
            unit_w = draw.textlength(unit, font=f_unit) if unit else 0
            total_cd_w = cd_w + unit_w
            cd_x = slot_x + (item_w - total_cd_w) // 2
            draw.text((cd_x, uy + 40), cd, font=f_count, fill=c_accent)
            if unit:
                draw.text((cd_x + cd_w + 2, uy + 58), unit, font=f_unit, fill=c_secondary)
            # 日期居中
            dt_w = draw.textlength(dt, font=f_date)
            draw.text((slot_x + (item_w - dt_w) // 2, uy + 100), dt, font=f_date, fill=c_secondary)

            if i < num - 1:
                div_x = start_x + (i + 1) * item_w
                draw.line([(div_x, y + 80), (div_x, y + section_h - 25)],
                          fill=(*c_divider, 150), width=1)

        return y + section_h + 20

    # ── Cities ────────────────────────────────────────────

    def _draw_cities(self, img: Image.Image, cities, y, card_h, card_gap):
        draw = ImageDraw.Draw(img, 'RGBA')
        mx = 60
        c_accent = self.colors.get("text_accent", (100, 130, 220))
        c_deco_blue = self.colors.get("deco_blue", (140, 190, 240))

        # 标题（楷体）
        f_sec = self._get_font(36, "kai")
        draw.text((mx, y), "城市天气", font=f_sec, fill=c_accent)
        draw.rounded_rectangle((mx, y + 44, mx + 60, y + 48), radius=2, fill=(*c_deco_blue, 120))
        y += 55

        card_w = (self.width - mx * 2 - card_gap) // 2
        pad = 20

        cards = []
        for idx in range(len(cities)):
            col = idx % 2
            row = idx // 2
            cx = mx + col * (card_w + card_gap)
            cy = y + row * (card_h + card_gap)
            cards.append((cx, cy, cx + card_w, cy + card_h))

        self._draw_glass_cards_batch(img, cards, radius=18, opacity=100, shadow_offset=8)
        draw = ImageDraw.Draw(img, 'RGBA')

        for idx, city in enumerate(cities):
            cx, cy, cx2, cy2 = cards[idx]
            self._draw_card_inner_decoration(draw, cx, cy, card_w, card_h, pad, idx)
            self._draw_city_card(draw, city, cx, cy, card_w, card_h, pad)

        total_rows = (len(cities) + 1) // 2
        return y + total_rows * (card_h + card_gap) + 10

    def _draw_city_card(self, draw, city, cx, cy, card_w, card_h, pad):
        c_title = self.colors.get("title", (50, 40, 100))
        c_primary = self.colors.get("text_primary", (35, 40, 65))
        c_secondary = self.colors.get("text_secondary", (110, 120, 150))
        c_tertiary = self.colors.get("text_tertiary", (155, 165, 190))
        c_divider = self.colors.get("divider", (210, 215, 235))
        c_warning = self.colors.get("warning", (220, 60, 70))

        fc = city.get("forecast", [])
        warns = city.get("warnings", [])

        # ── 上半部分布局 ──
        #  左列：城市名
        #  中列：气温 + 预警(如有，底纹贴分割线)
        #  右列：天气符号+文字(一行)、风力(下一行)
        #  ── 分割线 ──

        # 城市名（楷体加粗，上半区域垂直居中）
        f_city = self._get_font(66, "kai_bold")
        # 行楷本身已较粗，额外叠加一层半透明偏移实现加粗效果
        # 在下面的 draw.text 调用中处理
        # 气温（普通字体）
        f_temp = self._get_font(46)
        # 天气符号
        f_symbol = self._get_font(30, "emoji")
        # 天气文字
        f_wea = self._get_font(28)
        # 风力
        f_wind = self._get_font(26)
        # 预警
        f_warn = self._get_font(26)
        # 标签
        f_label = self._get_font(24)

        # 上半区域：从 cy 到 divider_y=cy+115，可用高度 115px
        top_content_h = 115
        divider_y = cy + top_content_h  # 分割线位置
        # 城市名字体高度约 64px，垂直居中
        city_font_h = 64
        city_y = cy + (top_content_h - city_font_h) // 2

        if len(fc) >= 2:
            tm = fc[1]

            # ── 左列：城市名（左移5px、下移5px）──
            draw.text((cx + pad + 15, city_y - 12), city["name"], font=f_city, fill=c_title)
            draw.text((cx + pad + 16, city_y - 12), city["name"], font=f_city, fill=c_title)

            # ── 中列：气温（上移）+ 预警 ──
            temp_x = cx + card_w // 3 + 20
            t_max = tm.get("tempMax", "--")
            t_min = tm.get("tempMin", "--")
            temp_t = f"{t_min}°/{t_max}°"
            temp_y = cy + 18  # 上移
            draw.text((temp_x, temp_y), temp_t, font=f_temp, fill=c_primary)

            # 预警（气温正下方，底纹下边贴着分割横线）
            if warns:
                warning_text = parse_warning_title(warns[0].get("title", ""))
                if warning_text:
                    warn_display = f"! {warning_text}"
                    max_warn_w = card_w // 3 + 60
                    while draw.textlength(warn_display, font=f_warn) > max_warn_w and len(warn_display) > 4:
                        warning_text = warning_text[:-1]
                        warn_display = f"! {warning_text}"
                    warn_tw = draw.textlength(warn_display, font=f_warn)
                    c_warning_bg = self.colors.get("warning_bg", (255, 238, 238))
                    # 底纹高40px，下边贴着 divider_y
                    box_h = 40
                    warn_box_top = divider_y - box_h
                    warn_box_bottom = divider_y - 2
                    self._rr(draw, (temp_x - 4, warn_box_top, temp_x + warn_tw + 8, warn_box_bottom), 6,
                             fill=(*c_warning_bg, 180))
                    # 文字垂直居中：字体 ascent=28, descent=7, 渲染高度35px
                    # 居中偏移 = (box_h - 35) / 2 + ascent偏移
                    text_y = warn_box_top + (box_h - 35) // 2 + 2
                    draw.text((temp_x, text_y), warn_display,
                              font=f_warn, fill=c_warning)

            # ── 右列：天气符号 + 文字（一行）、风力（下一行）──
            right_x = cx + card_w * 2 // 3 + 20
            weather_text = tm.get("textDay", "--")
            symbol = get_weather_symbol(weather_text)

            # 天气符号 + 天气文字
            draw.text((right_x, cy + 22), symbol, font=f_symbol, fill=c_secondary)
            sym_w = draw.textlength(symbol, font=f_symbol)
            draw.text((right_x + sym_w + 4, cy + 24), weather_text, font=f_wea, fill=c_secondary)

            # 风力（下一行）
            wd = tm.get("windDirDay", "")
            ws = tm.get("windScaleDay", "")
            wt = f"{wd}{ws}级" if wd else f"{ws}级"
            draw.text((right_x, cy + 60), wt, font=f_wind, fill=c_tertiary)

            # ── "明天" 标签（右上角）──
            label_text = "明天"
            lw = draw.textlength(label_text, font=f_label) + 16
            lx = cx + card_w - pad - lw
            ly = cy + 12
            c_tomorrow_bg = self.colors.get("tomorrow_bg", (248, 238, 255))
            c_tomorrow_text = self.colors.get("tomorrow_text", (120, 80, 180))
            self._rr(draw, (lx, ly, lx + lw, ly + 28), 8, fill=c_tomorrow_bg)
            draw.text((lx + 8, ly + 2), label_text, font=f_label, fill=c_tomorrow_text)

        # ── 分割线（固定位置）──
        draw.line([(cx + pad, divider_y), (cx + card_w - pad, divider_y)],
                  fill=(*c_divider, 150), width=1)

        # ── 下半部分：今天 + 后天（固定位置，不随预警移动）──
        # 槽位高度 = card_h - divider_y_offset - pad = 270 - 115 - 20 = 135px
        slot_top = divider_y + 8
        slot_bottom = cy + card_h - pad
        slot_h = slot_bottom - slot_top
        mid_x = cx + card_w // 2
        draw.line([(mid_x, slot_top), (mid_x, slot_bottom)], fill=(*c_divider, 150), width=1)

        half_w = (card_w - pad * 3) // 2
        lx = cx + pad
        rx = mid_x + pad

        # 内容高度：标签22 + 间距4 + 气温46 + 间距24 + 天气行30 = 126px
        # 垂直居中偏移
        content_h = 22 + 4 + 46 + 24 + 30
        y_offset = slot_top + (slot_h - content_h) // 2

        # 今天标签
        label_y = y_offset
        c_today_bg = self.colors.get("today_bg", (218, 245, 228))
        c_today_text = self.colors.get("today_text", (40, 140, 90))
        self._rr(draw, (lx, label_y, lx + 50, label_y + 22), 6, fill=c_today_bg)
        draw.text((lx + 4, label_y + 1), "今天", font=self._get_font(20), fill=c_today_text)

        # 今天内容：气温在标签下方4px，天气行在气温下方24px
        if len(fc) >= 1:
            self._draw_day_half(draw, fc[0], lx, label_y + 26, half_w)

        # 后天标签
        c_dayafter_bg = self.colors.get("dayafter_bg", (225, 238, 255))
        c_dayafter_text = self.colors.get("dayafter_text", (60, 110, 200))
        self._rr(draw, (rx, label_y, rx + 50, label_y + 22), 6, fill=c_dayafter_bg)
        draw.text((rx + 4, label_y + 1), "后天", font=self._get_font(20), fill=c_dayafter_text)

        if len(fc) >= 3:
            self._draw_day_half(draw, fc[2], rx, label_y + 26, half_w)

    def _draw_day_half(self, draw, day_data, x, y, width):
        """绘制单日天气详情（字号与明天一致）"""
        c_primary = self.colors.get("text_primary", (35, 40, 65))
        c_secondary = self.colors.get("text_secondary", (110, 120, 150))
        c_tertiary = self.colors.get("text_tertiary", (155, 165, 190))

        f_tmp = self._get_font(46)
        f_symbol = self._get_font(30, "emoji")
        f_wea = self._get_font(28)
        f_wind = self._get_font(26)

        temp = f"{day_data.get('tempMin','--')}°/{day_data.get('tempMax','--')}°"
        wea = day_data.get("textDay", "--")
        symbol = get_weather_symbol(wea)
        wd = day_data.get("windDirDay", "")
        ws = day_data.get("windScaleDay", "")
        wind = f"{wd}{ws}级" if wd else f"{ws}级"

        # 气温居中
        tb = draw.textbbox((0, 0), temp, font=f_tmp)
        tw = tb[2] - tb[0]
        draw.text((x + (width - tw) // 2, y), temp, font=f_tmp, fill=c_primary)

        # 天气符号 + 文字 + 风力 同一行居中（间距24px）
        sym_w = draw.textlength(symbol, font=f_symbol)
        wea_w = draw.textlength(wea, font=f_wea)
        wind_w = draw.textlength(wind, font=f_wind)
        total_w = sym_w + 4 + wea_w + 8 + wind_w
        start_x = x + (width - total_w) // 2
        line2_y = y + 70  # 气温高46 + 间距24 = 70
        draw.text((start_x, line2_y), symbol, font=f_symbol, fill=c_secondary)
        draw.text((start_x + sym_w + 4, line2_y + 2), wea, font=f_wea, fill=c_secondary)
        draw.text((start_x + sym_w + 4 + wea_w + 8, line2_y + 4), wind, font=f_wind, fill=c_tertiary)

    # ── Footer ────────────────────────────────────────────

    def _draw_footer(self, img: Image.Image, y):
        draw = ImageDraw.Draw(img, 'RGBA')
        mx = 60
        c_tertiary = self.colors.get("text_tertiary", (155, 165, 190))
        c_deco_purple = self.colors.get("deco_purple", (180, 160, 220))
        c_deco_green = self.colors.get("deco_green", (140, 210, 190))
        f = self._get_font(20)
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        text = f"数据来源：和风天气  ·  {now}"
        draw.text((mx, y), text, font=f, fill=c_tertiary)

        self._draw_gradient_line(draw, mx, y + 30, self.width - mx,
                                 c_deco_purple, c_deco_green, width=2)
        return y + 45
