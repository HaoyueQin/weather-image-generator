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

### API密钥配置（重要）

本项目使用和风天气API获取天气数据。为了安全起见，API密钥**不存储在代码仓库中**，而是单独存储在本地文件中。

**获取API密钥**：
1. 访问 https://dev.qweather.com/
2. 注册账号并登录
3. 在控制台创建新的API Key
4. 复制API Key

**配置API密钥**：

1. 复制 `.env.example` 为 `.env`：

```bash
cp .env.example .env
```

2. 在 `.env` 文件中填入你的真实 API Key：

```env
API_KEY=你的和风天气API密钥
```

3. 保存文件

**安全说明**：
- `.env` 文件已添加到 `.gitignore`，不会被上传到GitHub
- 项目提供了 `.env.example` 作为配置模板
- `config.py` 文件只包含公开配置（城市列表、颜色等），可以安全上传
- 请勿将API密钥硬编码在代码中或提交到版本控制

### 其他配置

`config.py` 文件包含以下公开配置：
- 城市列表
- 图片尺寸和颜色主题
- 字体配置
- 输出目录

你可以根据需要修改这些配置。

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
├── .gitignore          # Git忽略文件
├── .env.example        # API密钥配置模板（安全，可提交）
├── .env                # API密钥配置（本地文件，不上传）
├── README.md           # 项目说明文档
├── requirements.txt    # Python依赖
├── config.py           # 公开配置文件（城市、颜色等）
├── main.py             # 主程序入口
├── src/
│   ├── __init__.py
│   ├── weather_api.py      # 天气API接口
│   ├── image_generator.py  # 图像生成
│   └── date_utils.py       # 日期/节日/节气工具（sxtwl天文计算）
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