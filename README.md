# 天气预报图片生成器

获取 18 个城市的实时天气数据，自动生成精美的天气预报播报图片，并一键复制到剪贴板。

## 功能特点

- 和风天气 API 获取 18 个城市三天天气预报、实况天气、气象预警
- 自动生成包含天气符号、温度、风力、预警信息的播报图片
- 显示未来 5 个节日/节气倒计时（节气基于天文算法精确计算）
- 浅蓝+浅绿+浅紫渐变背景 + 毛玻璃卡片 + 装饰花纹
- 多字体排版：标题行楷、城市名楷体、英文 Georgia 衬线体
- 生成后自动复制到剪贴板，可直接粘贴到微信/QQ/钉钉
- 图片按月分类保存：`output/2026_06/weather_2026_06_25.png`

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置 API 密钥

复制 `.env.example` 为 `.env`，填入你的和风天气 API Key：

```bash
cp .env.example .env
```

在 `.env` 中填入：

```
API_KEY=你的和风天气API密钥
API_DOMAIN=nk7h2q8uut.re.qweatherapi.com
```

获取 API Key：https://dev.qweather.com/

### 3. 一键生成

**方式一：双击 `weather.bat`**

自动运行脚本，生成图片并复制到剪贴板。

**方式二：命令行**

```bash
python generate.py
```

**方式三：CLI 详细输出**

```bash
python main.py
```

## 项目结构

```
weather-image-generator/
├── .env.example        # API 密钥配置模板（可提交）
├── .env                # API 密钥配置（不提交）
├── .gitignore
├── README.md
├── config.py           # 公开配置（城市列表、配色、字体）
├── requirements.txt    # Python 依赖
├── main.py             # CLI 入口（详细输出）
├── generate.py         # 一键生成 + 复制到剪贴板
├── weather.bat         # 双击运行脚本
├── src/
│   ├── __init__.py
│   ├── weather_api.py      # 天气 API 接口（和风天气 v7）
│   ├── image_generator.py  # 图片生成（PIL 毛玻璃卡片）
│   └── date_utils.py       # 日期/农历/节气/节日（sxtwl 天文算法）
├── output/
│   └── 2026_06/
│       └── weather_2026_06_25.png
└── examples/               # 示例图片
```

## 支持的城市

18 个城市（硬编码在 `config.py`）：曲阜、青岛、昌平、新县、奎文、广州、张店、武汉、大连、保定、烟台、德州、南京、石家庄、潢川、海淀、瓯海、丰台。

## 技术栈

| 组件 | 技术 |
|------|------|
| 天气数据 | 和风天气 API v7 |
| 图片生成 | Pillow (PIL) |
| 节气计算 | sxtwl（寿星天文历） |
| 配置管理 | python-dotenv |
| 剪贴板 | pywin32 (win32clipboard) |

## 安全说明

- `.env` 文件已添加到 `.gitignore`，不会上传到 GitHub
- `.env.example` 作为配置模板，不含真实密钥
- 请勿将 API 密钥硬编码在代码中

## 许可证

MIT License
