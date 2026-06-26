"""
城市管理工具 - 图形界面版

功能：
- 查看当前城市列表
- 模糊搜索添加城市
- 删除城市
- 保存到 config.py

用法：python city_manager_gui.py
"""
import re
import csv
import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path

# 项目根目录
ROOT_DIR = Path(__file__).parent
CONFIG_PATH = ROOT_DIR / "config.py"
CSV_PATH = ROOT_DIR / "city_ids.csv"

# 颜色主题
COLORS = {
    "bg": "#f5f5f5",
    "card_bg": "#ffffff",
    "accent": "#4a90d9",
    "accent_hover": "#357abd",
    "danger": "#e74c3c",
    "danger_hover": "#c0392b",
    "success": "#27ae60",
    "text": "#2c3e50",
    "text_secondary": "#7f8c8d",
    "border": "#dce1e6",
}


class CityDatabase:
    """城市数据库"""

    def __init__(self):
        self.cities = []
        self._load()

    def _load(self):
        """加载城市数据库"""
        if not CSV_PATH.exists():
            return

        with open(CSV_PATH, "r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            self.cities = [
                {
                    "id": row["id"],
                    "name": row["name"],
                    "adm2": row.get("adm2", ""),
                    "adm1": row.get("adm1", ""),
                }
                for row in reader
            ]

    def search(self, query: str) -> list:
        """模糊搜索城市"""
        if not query.strip():
            return []

        suffixes = ["市", "区", "县", "省", "地区"]

        def normalize(text):
            return re.sub(r"[\s\-_,.，。、]+", "", text).lower()

        def remove_suffix(text):
            for s in suffixes:
                if text.endswith(s) and len(text) > len(s):
                    return text[: -len(s)]
            return text

        def remove_all_suffixes(text):
            changed = True
            while changed:
                changed = False
                for s in suffixes:
                    if text.endswith(s) and len(text) > len(s):
                        text = text[: -len(s)]
                        changed = True
                        break
            return text

        def is_main_city(c):
            return c["name"] == c["adm2"]

        qn = normalize(query)
        qns = remove_suffix(qn)
        results = []

        for city in self.cities:
            cn = normalize(city["name"])
            cns = remove_suffix(cn)
            a2 = normalize(city["adm2"])
            a2ns = remove_suffix(a2)
            a1 = normalize(city["adm1"])
            a1ns = remove_suffix(a1)

            score = 0
            matched = False

            # Rule 1: 完整路径
            fn = a1 + a2 + cn
            fns = a1ns + a2ns + cns
            if qn == fn or qns == fns:
                score = 120
                matched = True
            # Rule 2: 地级市+区县
            elif a2 and (qns == a2ns + cns):
                score = 115
                matched = True
            # Rule 3: 省+区县
            elif a1 and (qns == a1ns + cns):
                score = 110
                matched = True
            # Rule 4: 精确匹配城市名
            elif qn == cn:
                score = 110
                matched = True
            # Rule 5: query去后缀 == city_name去后缀
            elif qns == cns:
                score = 95
                matched = True
            # Rule 6: 查询以城市名结尾
            elif len(cns) >= 2 and qns.endswith(cns):
                prefix = qns[: -len(cns)]
                pns = remove_all_suffixes(prefix)
                if pns and a2 and pns == a2ns:
                    score = 115
                elif pns and a1 and pns == a1ns:
                    score = 114
                elif pns and a2 and (pns in a2ns or a2ns in pns):
                    score = 112
                elif pns and a1 and (pns in a1ns or a1ns in pns):
                    score = 111
                else:
                    score = 70 + len(cns) * 3
                matched = True
            # Rule 7: 查询包含城市名
            elif len(cns) >= 2 and cns in qns:
                score = 70 + len(cns) * 3
                matched = True

            if matched:
                type_bonus = 10 if is_main_city(city) else 0
                results.append((score + type_bonus, city))

        results.sort(key=lambda x: -x[0])
        return [city for _, city in results[:20]]


class ConfigManager:
    """配置文件管理"""

    @staticmethod
    def load_cities() -> dict:
        """从 config.py 加载城市"""
        if not CONFIG_PATH.exists():
            return {}

        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            content = f.read()

        match = re.search(r"CITIES\s*=\s*\{([^}]+)\}", content, re.DOTALL)
        if not match:
            return {}

        cities = {}
        for line in match.group(1).split("\n"):
            m = re.search(r"'(\d{9})'\s*:\s*'([^']+)'", line)
            if m:
                cities[m.group(1)] = m.group(2)
        return cities

    @staticmethod
    def save_cities(cities: dict):
        """保存城市到 config.py"""
        if not CONFIG_PATH.exists():
            return

        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            content = f.read()

        cities_lines = [f"    '{cid}': '{name}'," for cid, name in cities.items()]
        new_cities_str = "CITIES = {\n" + "\n".join(cities_lines) + "\n}"

        content = re.sub(r"CITIES\s*=\s*\{[^}]+\}", new_cities_str, content, flags=re.DOTALL)
        content = re.sub(r"# 城市配置（\d+ 个城市）", f"# 城市配置（{len(cities)} 个城市）", content)

        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            f.write(content)


class CityManagerGUI:
    """城市管理 GUI"""

    def __init__(self):
        self.db = CityDatabase()
        self.config_cities = ConfigManager.load_cities()

        self.root = tk.Tk()
        self.root.title("天气预报 - 城市管理")
        self.root.geometry("900x640")
        self.root.configure(bg=COLORS["bg"])
        self.root.resizable(False, False)

        self._build_ui()

    def _build_ui(self):
        """构建界面"""
        # 主容器
        main = ttk.Frame(self.root, padding=20)
        main.pack(fill=tk.BOTH, expand=True)

        # 标题
        title = ttk.Label(main, text="城市管理", font=("Microsoft YaHei", 16, "bold"))
        title.pack(anchor=tk.W, pady=(0, 15))

        # 左右分栏
        paned = ttk.PanedWindow(main, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True)

        # === 左侧：搜索 + 添加 ===
        left = ttk.LabelFrame(paned, text="搜索并添加城市", padding=10)
        paned.add(left, weight=1)

        # 搜索框
        search_frame = ttk.Frame(left)
        search_frame.pack(fill=tk.X, pady=(0, 10))

        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *_: self._on_search())
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, font=("Microsoft YaHei", 11))
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        search_entry.insert(0, "")
        search_entry.bind("<Return>", lambda e: self._on_search())

        # 搜索结果列表
        result_frame = ttk.Frame(left)
        result_frame.pack(fill=tk.BOTH, expand=True)

        columns = ("id", "name", "adm2", "adm1")
        self.result_tree = ttk.Treeview(result_frame, columns=columns, show="headings", height=15)
        self.result_tree.heading("id", text="ID")
        self.result_tree.heading("name", text="区县")
        self.result_tree.heading("adm2", text="地级市")
        self.result_tree.heading("adm1", text="省份")
        self.result_tree.column("id", width=90, minwidth=90)
        self.result_tree.column("name", width=80, minwidth=60)
        self.result_tree.column("adm2", width=80, minwidth=60)
        self.result_tree.column("adm1", width=100, minwidth=80)

        scrollbar = ttk.Scrollbar(result_frame, orient=tk.VERTICAL, command=self.result_tree.yview)
        self.result_tree.configure(yscrollcommand=scrollbar.set)
        self.result_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # 添加按钮
        add_btn = ttk.Button(left, text="添加选中城市", command=self._add_selected)
        add_btn.pack(fill=tk.X, pady=(10, 0))

        # === 右侧：当前城市列表 ===
        right = ttk.LabelFrame(paned, text="当前城市列表", padding=10)
        paned.add(right, weight=1)

        # 当前城市列表
        current_frame = ttk.Frame(right)
        current_frame.pack(fill=tk.BOTH, expand=True)

        columns2 = ("idx", "id", "name")
        self.current_tree = ttk.Treeview(current_frame, columns=columns2, show="headings", height=15)
        self.current_tree.heading("idx", text="#")
        self.current_tree.heading("id", text="LocationID")
        self.current_tree.heading("name", text="城市名称")
        self.current_tree.column("idx", width=30, minwidth=30)
        self.current_tree.column("id", width=100, minwidth=90)
        self.current_tree.column("name", width=120, minwidth=80)

        scrollbar2 = ttk.Scrollbar(current_frame, orient=tk.VERTICAL, command=self.current_tree.yview)
        self.current_tree.configure(yscrollcommand=scrollbar2.set)
        self.current_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar2.pack(side=tk.RIGHT, fill=tk.Y)

        # 删除按钮
        btn_frame = ttk.Frame(right)
        btn_frame.pack(fill=tk.X, pady=(10, 0))

        remove_btn = ttk.Button(btn_frame, text="删除选中城市", command=self._remove_selected)
        remove_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))

        save_btn = ttk.Button(btn_frame, text="保存到 config.py", command=self._save)
        save_btn.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # 底部状态栏
        self.status_var = tk.StringVar(value=f"当前 {len(self.config_cities)} 个城市")
        status_bar = ttk.Label(main, textvariable=self.status_var, foreground=COLORS["text_secondary"])
        status_bar.pack(anchor=tk.W, pady=(10, 0))

        # 初始化列表
        self._refresh_current_list()

    def _on_search(self):
        """搜索框内容变化"""
        query = self.search_var.get().strip()
        if not query:
            self._clear_results()
            return

        results = self.db.search(query)
        self._show_results(results)

    def _clear_results(self):
        """清空搜索结果"""
        for item in self.result_tree.get_children():
            self.result_tree.delete(item)

    def _show_results(self, results: list):
        """显示搜索结果"""
        self._clear_results()
        for city in results:
            added = city["id"] in self.config_cities
            tag = "added" if added else ""
            self.result_tree.insert(
                "", tk.END, values=(city["id"], city["name"], city["adm2"], city["adm1"]), tags=(tag,)
            )
        self.result_tree.tag_configure("added", foreground=COLORS["success"])

    def _add_selected(self):
        """添加选中的城市"""
        selected = self.result_tree.selection()
        if not selected:
            messagebox.showinfo("提示", "请先在左侧搜索结果中选择要添加的城市")
            return

        added_count = 0
        for item in selected:
            values = self.result_tree.item(item, "values")
            city_id, city_name = values[0], values[1]
            if city_id not in self.config_cities:
                self.config_cities[city_id] = city_name
                added_count += 1

        if added_count > 0:
            self._refresh_current_list()
            self._on_search()  # 刷新搜索结果（显示已添加标记）
            self.status_var.set(f"已添加 {added_count} 个城市，共 {len(self.config_cities)} 个")
        else:
            messagebox.showinfo("提示", "选中的城市已在列表中")

    def _remove_selected(self):
        """删除选中的城市"""
        selected = self.current_tree.selection()
        if not selected:
            messagebox.showinfo("提示", "请先在右侧列表中选择要删除的城市")
            return

        removed_count = 0
        for item in selected:
            values = self.current_tree.item(item, "values")
            city_id = values[1]
            if city_id in self.config_cities:
                del self.config_cities[city_id]
                removed_count += 1

        if removed_count > 0:
            self._refresh_current_list()
            self._on_search()  # 刷新搜索结果
            self.status_var.set(f"已删除 {removed_count} 个城市，共 {len(self.config_cities)} 个")

    def _refresh_current_list(self):
        """刷新当前城市列表"""
        for item in self.current_tree.get_children():
            self.current_tree.delete(item)

        for i, (city_id, city_name) in enumerate(self.config_cities.items(), 1):
            self.current_tree.insert("", tk.END, values=(i, city_id, city_name))

    def _save(self):
        """保存到配置文件"""
        ConfigManager.save_cities(self.config_cities)
        self.status_var.set(f"已保存 {len(self.config_cities)} 个城市到 config.py")
        messagebox.showinfo("保存成功", f"已保存 {len(self.config_cities)} 个城市到 config.py")

    def run(self):
        """运行 GUI"""
        self.root.mainloop()


if __name__ == "__main__":
    app = CityManagerGUI()
    app.run()
