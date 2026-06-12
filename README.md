# 天气预报播报图片生成器

一个简单的天气预报播报图片生成工具，可以获取多个城市的实时天气信息，并生成精美的天气预报播报图片。

## 功能特点

- 支持选择多个城市获取天气信息
- 自动生成包含天气图标、温度、城市名的播报图片
- 显示未来节日/节气倒计时
- 显示天气预警信息
- 浅色主题，清晰布局
- 支持三天天气预报（今天、明天、后天）

## 安装依赖

```bash
pip install -r requirements.txt
```

## 配置

1. 复制 `config.py.example` 为 `config.py`
2. 在 `config.py` 中填入你的天气API密钥
3. 可选：调整其他配置项

## 使用方法

### 命令行模式

```bash
# 基本用法
python main.py

# 指定输出文件
python main.py --output weather.png
```

### 作为模块使用

```python
from src.weather_api import WeatherAPI
from src.image_generator import WeatherImageGenerator

# 获取天气数据
api = WeatherAPI()
weather_data = api.get_weather("北京")

# 生成图片
generator = WeatherImageGenerator()
generator.generate_image([weather_data], "weather.png")
```

## 项目结构

```
weather-image-generator/
├── .gitignore
├── README.md
├── requirements.txt
├── config.py               # 配置文件
├── main.py                 # 主程序入口
├── src/
│   ├── __init__.py
│   ├── weather_api.py      # 天气API接口
│   ├── image_generator.py  # 图像生成
│   └── date_utils.py       # 日期/节日工具
├── output/                 # 生成的图片
└── examples/               # 示例图片
```

## 支持的城市

支持全球主要城市，中文或英文名称均可：
- 中国：北京、上海、广州、深圳、杭州等
- 国际：Tokyo、New York、London、Paris等

## 天气预警

支持显示以下类型的天气预警：
- 高温预警
- 暴雨预警
- 雷电预警
- 大风预警
- 等等

## 许可证

MIT License