@echo off
chcp 65001 >nul
echo ========================================
echo  天气预报播报图片生成器 - 打包脚本
echo ========================================
echo.

:: 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到Python，请先安装Python
    pause
    exit /b 1
)

:: 检查PyInstaller是否安装
pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo [提示] 正在安装PyInstaller...
    pip install pyinstaller
)

:: 检查依赖
echo [1/4] 检查并安装依赖...
pip install -r requirements.txt
pip install Pillow
pip install pywin32

:: 清理旧的构建文件
echo [2/4] 清理旧的构建文件...
if exist dist rmdir /s /q dist
if exist build rmdir /s /q build

:: 打包
echo [3/4] 正在打包为exe...
pyinstaller ^
    --onefile ^
    --windowed ^
    --name "天气预报播报图片生成器" ^
    --icon=NUL ^
    --add-data "config.py;." ^
    --add-data "src;src" ^
    --hidden-import=PIL ^
    --hidden-import=PIL.Image ^
    --hidden-import=PIL.ImageTk ^
    --hidden-import=tkinter ^
    --hidden-import=tkinter.ttk ^
    --hidden-import=win32clipboard ^
    --hidden-import=win32con ^
    --hidden-import=dotenv ^
    --hidden-import=sxtwl ^
    --noconfirm ^
    weather_gui.py

:: 完成
echo [4/4] 打包完成！
echo.
echo ========================================
echo  输出文件位置: dist\天气预报播报图片生成器.exe
echo ========================================
echo.

:: 打开输出目录
explorer dist

pause