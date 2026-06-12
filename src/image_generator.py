"""
天气图片生成模块 - 最终版
"""

from PIL import Image, ImageDraw, ImageFont
from typing import Dict, List, Tuple, Any
from datetime import datetime
import os


class WeatherImageGenerator:

    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.width = self.config.get("width", 1440)
        self.colors = self.config.get("colors", {})
        self._fonts = {}

    def _get_font(self, size: int) -> ImageFont.FreeTypeFont:
        if size not in self._fonts:
            font_path = self.config.get("font_path")
            try:
                if font_path and os.path.exists(font_path):
                    if font_path.lower().endswith('.ttc'):
                        self._fonts[size] = ImageFont.truetype(font_path, size, index=0)
                    else:
                        self._fonts[size] = ImageFont.truetype(font_path, size)
                else:
                    self._fonts[size] = ImageFont.truetype("arial.ttf", size)
            except Exception:
                self._fonts[size] = ImageFont.load_default()
        return self._fonts[size]

    def _rr(self, draw, xy, r, fill=None, outline=None, width=1):
        draw.rounded_rectangle(xy, radius=r, fill=fill, outline=outline, width=width)

    def generate_image(self, date_info, cities_weather, upcoming_events, output_path):
        try:
            num = len(cities_weather)
            card_h = 270
            card_gap = 10
            rows = (num + 1) // 2

            total_h = 150 + 240 + 55 + rows * (card_h + card_gap) + 50 + 80
            img = Image.new("RGB", (self.width, total_h), self.colors["background"])
            draw = ImageDraw.Draw(img)

            y = 40
            y = self._draw_header(draw, date_info, y)
            y = self._draw_events(draw, upcoming_events, y)
            y = self._draw_cities(draw, cities_weather, y, card_h, card_gap)
            y = self._draw_footer(draw, y)

            img = img.crop((0, 0, self.width, min(y + 40, total_h)))
            os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
            img.save(output_path, quality=95)
            return True
        except Exception as e:
            print(f"Error: {e}")
            import traceback; traceback.print_exc()
            return False

    def _draw_header(self, draw, date_info, y):
        f_title = self._get_font(80)
        f_date = self._get_font(48)
        f_small = self._get_font(30)

        draw.text((80, y + 15), "天气预报", font=f_title, fill=self.colors["title"])

        sx = self.width - 80
        date_text = f"{date_info['solar_date']} {date_info['weekday']}"
        draw.text((sx, y + 20), date_text, font=f_date, fill=self.colors["text_primary"], anchor="ra")
        draw.text((sx, y + 75), f"农历 {date_info['cyclical_year']}", font=f_small, fill=self.colors["text_secondary"], anchor="ra")

        y += 140
        draw.line([(80, y), (self.width - 80, y)], fill=self.colors["divider"], width=3)
        return y + 20

    def _draw_events(self, draw, events, y):
        if not events:
            return y

        f_title = self._get_font(38)
        f_name = self._get_font(34)
        f_count = self._get_font(32)
        f_date = self._get_font(28)

        section_h = 230
        self._rr(draw, (80, y, self.width - 80, y + section_h), 16, fill=self.colors["section_bg"])

        y += 12
        draw.text((120, y), "未来节日/节气", font=f_title, fill=self.colors["text_accent"])
        y += 55

        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        num = min(len(events), 5)
        spacing = (self.width - 200) // num

        for i, (ed, en) in enumerate(events[:5]):
            dl = (ed - today).days
            cd = f"{dl}天后" if dl > 0 else "今天"
            dt = ed.strftime("%m月%d日")
            ux = 120 + i * spacing

            draw.text((ux, y), en, font=f_name, fill=self.colors["text_primary"])
            draw.text((ux, y + 40), cd, font=f_count, fill=self.colors["text_accent"])
            draw.text((ux, y + 76), dt, font=f_date, fill=self.colors["text_secondary"])

        draw.line([(100, y + 120), (self.width - 100, y + 120)], fill=self.colors["divider"], width=1)
        return y + 135

    def _draw_cities(self, draw, cities, y, card_h, card_gap):
        f_sec = self._get_font(38)
        draw.text((80, y), "各城市天气预报", font=f_sec, fill=self.colors["text_accent"])
        y += 50

        mx = 80
        card_w = (self.width - mx * 2 - card_gap) // 2
        pad = 16

        for idx, city in enumerate(cities):
            col = idx % 2
            row = idx // 2
            cx = mx + col * (card_w + card_gap)
            cy = y + row * (card_h + card_gap)

            self._rr(draw, (cx, cy, cx + card_w, cy + card_h), 12,
                      fill=self.colors["card_bg"], outline=self.colors["card_border"], width=1)

            fc = city.get("forecast", [])
            warns = city.get("warnings", [])
            wh = 28 if warns else 0

            # ===== 上半部分 =====
            top_h = 100
            draw.line([(cx + pad, cy + top_h), (cx + card_w - pad, cy + top_h)],
                      fill=self.colors["divider"], width=1)

            if len(fc) >= 2:
                tm = fc[1]
                f_city = self._get_font(52)
                f_temp = self._get_font(48)
                f_wea = self._get_font(34)
                f_wind = self._get_font(28)
                f_label = self._get_font(24)

                mid_y = cy + top_h // 2

                # 城市名
                draw.text((cx + pad, mid_y - 26), city["name"], font=f_city, fill=self.colors["title"])

                # 气温
                t_max = tm.get("tempMax", "--")
                t_min = tm.get("tempMin", "--")
                temp_t = f"{t_min}°/{t_max}°"
                draw.text((cx + card_w // 2 - 140, mid_y - 24), temp_t, font=f_temp, fill=self.colors["text_primary"])

                # 天气+风力
                wx = cx + card_w // 2 + 70
                draw.text((wx, mid_y - 28), tm.get("textDay", "--"), font=f_wea, fill=self.colors["text_secondary"])
                wd = tm.get("windDirDay", "")
                ws = tm.get("windScaleDay", "")
                wt = f"{wd}{ws}级" if wd else f"{ws}级"
                draw.text((wx, mid_y + 10), wt, font=f_wind, fill=self.colors["text_secondary"])

                # 明天标签
                self._rr(draw, (cx + card_w - 65, cy + 10, cx + card_w - pad, cy + 36), 5,
                          fill=self.colors["tomorrow_bg"])
                draw.text((cx + card_w - 61, cy + 11), "明天", font=f_label, fill=self.colors["text_secondary"])

            # 预警
            if warns:
                draw.line([(cx + pad, cy + top_h), (cx + card_w - pad, cy + top_h)],
                          fill=self.colors["warning"], width=2)
                wt = warns[0].get("title", "预警")[:28]
                draw.text((cx + pad, cy + top_h + 3), wt, font=self._get_font(20), fill=self.colors["warning"])

            # ===== 下半部分：今天 + 后天 =====
            bot_y = cy + top_h + wh + 8
            mid_x = cx + card_w // 2
            draw.line([(mid_x, bot_y), (mid_x, cy + card_h - pad)], fill=self.colors["divider"], width=1)

            half_w = (card_w - pad * 3) // 2
            lx = cx + pad
            rx = mid_x + pad

            # 左半格：今天
            self._rr(draw, (lx, bot_y, lx + 50, bot_y + 20), 4, fill=self.colors["today_bg"])
            draw.text((lx + 4, bot_y + 1), "今天", font=self._get_font(20), fill=self.colors["success"])

            if len(fc) >= 1:
                td = fc[0]
                f_tmp = self._get_font(40)
                f_wt = self._get_font(28)
                f_wd = self._get_font(24)

                d_temp = f"{td.get('tempMin','--')}°/{td.get('tempMax','--')}°"
                d_wea = td.get("textDay", "--")
                d_wd = td.get("windDirDay", "")
                d_ws = td.get("windScaleDay", "")
                d_wind = f"{d_wd}{d_ws}级" if d_wd else f"{d_ws}级"

                # 气温 - 居中
                tb = draw.textbbox((0, 0), d_temp, font=f_tmp)
                tw = tb[2] - tb[0]
                draw.text((lx + (half_w - tw) // 2, bot_y + 28), d_temp, font=f_tmp, fill=self.colors["text_primary"])

                # 天气+风力 - 同一行，左右分布
                weather_wind = f"{d_wea}  {d_wind}"
                ww = draw.textbbox((0, 0), weather_wind, font=f_wt)
                www = ww[2] - ww[0]
                draw.text((lx + (half_w - www) // 2, bot_y + 75), weather_wind, font=f_wt, fill=self.colors["text_secondary"])

            # 右半格：后天
            self._rr(draw, (rx, bot_y, rx + 50, bot_y + 20), 4, fill=self.colors["dayafter_bg"])
            draw.text((rx + 4, bot_y + 1), "后天", font=self._get_font(20), fill=self.colors["text_accent"])

            if len(fc) >= 3:
                da = fc[2]
                f_tmp = self._get_font(40)
                f_wt = self._get_font(28)
                f_wd = self._get_font(24)

                da_temp = f"{da.get('tempMin','--')}°/{da.get('tempMax','--')}°"
                da_wea = da.get("textDay", "--")
                da_wd = da.get("windDirDay", "")
                da_ws = da.get("windScaleDay", "")
                da_wind = f"{da_wd}{da_ws}级" if da_wd else f"{da_ws}级"

                tb = draw.textbbox((0, 0), da_temp, font=f_tmp)
                tw = tb[2] - tb[0]
                draw.text((rx + (half_w - tw) // 2, bot_y + 28), da_temp, font=f_tmp, fill=self.colors["text_primary"])

                weather_wind = f"{da_wea}  {da_wind}"
                ww = draw.textbbox((0, 0), weather_wind, font=f_wt)
                www = ww[2] - ww[0]
                draw.text((rx + (half_w - www) // 2, bot_y + 75), weather_wind, font=f_wt, fill=self.colors["text_secondary"])

        total_rows = (len(cities) + 1) // 2
        return y + total_rows * (card_h + card_gap) + 20

    def _draw_footer(self, draw, y):
        f = self._get_font(22)
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        draw.text((80, y), f"数据来源: 和风天气 | 生成时间: {now}", font=f, fill=self.colors["text_secondary"])
        return y + 35
