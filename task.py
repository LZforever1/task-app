import os
import json
import sys
import re
import random
from datetime import date, datetime, timedelta
from collections import Counter

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.gridlayout import GridLayout
from kivy.uix.checkbox import CheckBox
from kivy.uix.image import Image
from kivy.uix.floatlayout import FloatLayout
from kivy.core.window import Window
from kivy.utils import platform
from kivy.clock import Clock
from kivy.graphics import Color, RoundedRectangle, Line
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.core.text import LabelBase
from kivy.lang import Builder
from kivy.metrics import dp

# ========== 中文字体 ==========
if platform == "win":
    font_paths = [
        "C:/Windows/Fonts/msyh.ttc",
        "C:/Windows/Fonts/simhei.ttf",
        "C:/Windows/Fonts/simsun.ttc",
    ]
    for fp in font_paths:
        if os.path.exists(fp):
            try:
                LabelBase.register("ChineseFont", fp)
                break
            except:
                continue
elif platform == "android":
    font_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "msyh.ttc")
    if os.path.exists(font_path):
        LabelBase.register("ChineseFont", font_path)
    else:
        LabelBase.register("ChineseFont", "Roboto")

if platform == "android":
    from jnius import autoclass
    PythonActivity = autoclass("org.kivy.android.PythonActivity")
    from android import activity
    Intent = autoclass('android.content.Intent')
    FileOutputStream = autoclass('java.io.FileOutputStream')
    Context = autoclass('android.content.Context')
    NotificationBuilder = autoclass('android.app.Notification$Builder')

# ========== 全局样式 ==========
Builder.load_string('''
<Button>:
    background_normal: ''
    background_down: ''
    font_size: '14sp'
    size_hint_y: None
    height: '44dp'
    font_name: 'ChineseFont'

<TextInput>:
    background_normal: ''
    background_active: ''
    background_color: (0.95, 0.95, 0.96, 1)
    foreground_color: (0.2, 0.2, 0.2, 1)
    cursor_color: (0.13, 0.45, 0.75, 1)
    font_size: '14sp'
    padding: [12, 0]
    multiline: False
    font_name: 'ChineseFont'

<Popup>:
    background: ''
    background_color: (0.97, 0.97, 0.98, 1)
    title_color: (0.2, 0.2, 0.2, 1)
    title_size: '16sp'
    separator_color: (0.9, 0.9, 0.92, 1)
''')

# ========== 设计常量 ==========
COLOR_PRIMARY = (0.13, 0.44, 0.76, 1)
COLOR_BG = (0.97, 0.97, 0.98, 1)
COLOR_CARD = (1, 1, 1, 1)
COLOR_TEXT = (0.2, 0.2, 0.2, 1)
COLOR_TEXT_GRAY = (0.53, 0.53, 0.53, 1)
COLOR_TEXT_LIGHT = (0.67, 0.67, 0.67, 1)
COLOR_LINE = (0.9, 0.9, 0.92, 1)
COLOR_INPUT_BG = (0.95, 0.95, 0.96, 1)
COLOR_SUCCESS = (0.3, 0.6, 0.35, 1)
COLOR_PIN_BG = (0.98, 0.96, 0.9, 1)

SPACING_XL = 20
SPACING_MD = 12
SPACING_SM = 6
RADIUS_MD = 8
RADIUS_LG = 16
RADIUS_PILL = 22

FONT_TITLE = '18sp'
FONT_BODY = '13sp'
FONT_CAPTION = '11sp'
FONT_SMALL = '10sp'

WEEKDAYS = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]

# ========== 数据 ==========
DATA_FILE = "tasks.json"
BACKUP_FILE = "tasks_backup.json"

def get_data_path():
    if platform == "android":
        # 使用 Kivy 用户目录，避免导入 app_storage_path 可能失败
        user_data_dir = os.environ.get('ANDROID_PRIVATE', '')
        return os.path.join(user_data_dir, DATA_FILE)
    return DATA_FILE

def get_backup_path():
    if platform == "android":
        user_data_dir = os.environ.get('ANDROID_PRIVATE', '')
        return os.path.join(user_data_dir, BACKUP_FILE)
    return BACKUP_FILE

def get_image_dir():
    if platform == "android":
        user_data_dir = os.environ.get('ANDROID_PRIVATE', '')
        img_dir = os.path.join(user_data_dir, "images")
    else:
        img_dir = "images"
    if not os.path.exists(img_dir):
        os.makedirs(img_dir)
    return img_dir

def load_data():
    path = get_data_path()
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_data(data):
    try:
        path = get_data_path()
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"保存数据失败: {e}")

def extract_keywords(text, top_n=3):
    cleaned = re.sub(r'[^\w\u4e00-\u9fff]', ' ', text)
    words = [w for w in cleaned.split() if len(w) >= 2]
    if not words:
        return "无关键词"
    return "、".join([w for w, _ in Counter(words).most_common(top_n)])

# ========== 基础组件 ==========
class TextButton(Button):
    def __init__(self, text_color=COLOR_TEXT_GRAY, **kwargs):
        super().__init__(**kwargs)
        self.background_color = (0, 0, 0, 0)
        self.color = text_color

class RoundedButton(Button):
    def __init__(self, bg_color=COLOR_PRIMARY, text_color=COLOR_CARD, radius=RADIUS_MD, **kwargs):
        super().__init__(**kwargs)
        self.background_color = (0, 0, 0, 0)
        self.color = text_color
        with self.canvas.before:
            Color(*bg_color)
            self.rect = RoundedRectangle(radius=[radius], pos=self.pos, size=self.size)
        self.bind(pos=self.update_rect, size=self.update_rect)

    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size

# ========== 基础弹窗 ==========
class BasePopup(Popup):
    def __init__(self, title_text, content_widget, buttons=None, **kwargs):
        super().__init__(**kwargs)
        self.title = ""
        self.auto_dismiss = False
        self.size_hint = (0.85, None)
        self.height = dp(300)

        main_layout = BoxLayout(orientation="vertical", padding=[25, 25, 25, 25], spacing=20)

        title_row = BoxLayout(orientation="horizontal", size_hint_y=None, height=dp(30))
        title_label = Label(
            text=title_text,
            font_size="18sp",
            bold=True,
            color=COLOR_TEXT,
            halign="left",
            valign="middle",
            text_size=(None, dp(30))
        )
        title_row.add_widget(title_label)
        close_btn = TextButton(text="关闭", font_size="14sp", size_hint_x=None, width=dp(50), text_color=COLOR_TEXT_GRAY)
        close_btn.bind(on_press=self.dismiss)
        title_row.add_widget(close_btn)
        main_layout.add_widget(title_row)

        main_layout.add_widget(content_widget)

        if buttons:
            btn_row = BoxLayout(orientation="horizontal", size_hint_y=None, height=dp(44), spacing=10)
            for btn_text, btn_color, btn_callback in buttons:
                btn = RoundedButton(
                    text=btn_text,
                    bg_color=btn_color,
                    text_color=COLOR_CARD if btn_color == COLOR_PRIMARY else COLOR_TEXT,
                    radius=RADIUS_PILL,
                    font_size="15sp"
                )
                btn.bind(on_press=btn_callback)
                btn_row.add_widget(btn)
            main_layout.add_widget(btn_row)

        self.content = main_layout

# ========== 任务行 ==========
class TaskRow(BoxLayout):
    def __init__(self, content, status, index, callback, has_image=False, pinned=False, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "horizontal"
        self.size_hint_y = None
        self.height = 50
        self.padding = [15, 0, 15, 0]
        self.spacing = 10
        self.index = index
        self.callback = callback

        bg = COLOR_PIN_BG if pinned else COLOR_CARD
        with self.canvas.before:
            Color(*bg)
            self.rect = RoundedRectangle(radius=[6], pos=self.pos, size=self.size)
            if status == "done":
                line_color = COLOR_SUCCESS
            elif status == "handover":
                line_color = COLOR_PRIMARY
            else:
                line_color = COLOR_LINE
            Color(*line_color)
            self.status_line = RoundedRectangle(radius=[2], pos=(self.x + 5, self.y + 5), size=(4, self.height - 10))
        self.bind(pos=self.update_rect, size=self.update_rect)

        self.checkbox = CheckBox(
            active=(status != "pending"),
            size_hint=(None, None),
            size=(24, 24),
            pos_hint={'center_y': 0.5},
            color=COLOR_PRIMARY
        )
        self.checkbox.bind(active=self.on_checkbox_active)
        self.add_widget(self.checkbox)

        if status == "done":
            text_color = COLOR_TEXT_LIGHT
        elif status == "handover":
            text_color = COLOR_PRIMARY
        else:
            text_color = COLOR_TEXT

        display = content
        if pinned:
            display = "[顶] " + display
        if has_image:
            display += " [图]"

        self.content_btn = Button(
            text=display,
            font_size=FONT_BODY,
            halign="left",
            valign="middle",
            color=text_color,
            background_normal='',
            background_color=(0,0,0,0),
            size_hint_x=1
        )
        self.content_btn.bind(size=lambda instance, value: setattr(instance, 'text_size', (value[0], self.height)))
        self.content_btn.bind(on_release=lambda x: self.callback(self.index, "detail"))
        self.add_widget(self.content_btn)

        if status == "done":
            with self.content_btn.canvas.after:
                Color(0.6, 0.6, 0.6, 0.8)
                self.strike_line = Line(points=[self.content_btn.x, self.content_btn.center_y, self.content_btn.right, self.content_btn.center_y], width=1)
                self.content_btn.bind(pos=self.update_strike, size=self.update_strike)

        action_box = BoxLayout(orientation="horizontal", size_hint_x=None, width=150, spacing=2)
        pin_btn = TextButton(text="置顶", font_size=FONT_CAPTION, size_hint_x=None, width=45, text_color=COLOR_TEXT_GRAY)
        pin_btn.bind(on_release=lambda x: self.callback(self.index, "pin"))
        action_box.add_widget(pin_btn)

        edit_btn = TextButton(text="编辑", font_size=FONT_CAPTION, size_hint_x=None, width=45, text_color=COLOR_TEXT_GRAY)
        edit_btn.bind(on_release=lambda x: self.callback(self.index, "edit"))
        action_box.add_widget(edit_btn)

        del_btn = TextButton(text="删除", font_size=FONT_CAPTION, size_hint_x=None, width=45, text_color=(0.7,0.4,0.4,1))
        del_btn.bind(on_release=lambda x: self.callback(self.index, "delete"))
        action_box.add_widget(del_btn)

        self.add_widget(action_box)

    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size
        if hasattr(self, 'status_line'):
            self.status_line.pos = (self.x + 5, self.y + 5)
            self.status_line.size = (4, self.height - 10)

    def update_strike(self, *args):
        if hasattr(self, 'strike_line'):
            self.strike_line.points = [self.content_btn.x, self.content_btn.center_y, self.content_btn.right, self.content_btn.center_y]

    def on_checkbox_active(self, checkbox, value):
        if value:
            self.callback(self.index, "ask_status")
        else:
            self.callback(self.index, "pending")

    def on_touch_down(self, touch):
        return super().on_touch_down(touch)

# ========== 筛选弹窗 ==========
class FilterPopup(BasePopup):
    def __init__(self, current_filter, on_select, **kwargs):
        self.current_filter = current_filter
        self.on_select = on_select
        content = BoxLayout(orientation="vertical", spacing=10, padding=[0, 10, 0, 0])
        filters = ["全部", "未完成", "已完成", "已交接"]
        for f in filters:
            btn = RoundedButton(
                text=f,
                bg_color=COLOR_PRIMARY if f == current_filter else COLOR_INPUT_BG,
                text_color=COLOR_CARD if f == current_filter else COLOR_TEXT,
                radius=RADIUS_MD,
                font_size=FONT_BODY,
                size_hint_y=None,
                height=44
            )
            btn.bind(on_release=lambda instance, text=f: self.select(text))
            content.add_widget(btn)
        super().__init__(title_text="筛选任务", content_widget=content, buttons=None, **kwargs)
        self.height = dp(280)

    def select(self, filter_text):
        self.on_select(filter_text)
        self.dismiss()

# ========== 主页面 ==========
class MainScreen(Screen):
    def __init__(self, app, **kwargs):
        super().__init__(**kwargs)
        self.app = app
        self.current_filter = "全部"
        self.search_text = ""
        self.current_image_path = None
        self.build_ui()

    def build_ui(self):
        root = BoxLayout(orientation="vertical", padding=[SPACING_XL, 16, SPACING_XL, 16], spacing=SPACING_SM)

        today = date.today()
        weekday = WEEKDAYS[today.weekday()]

        # 日期标题
        title_area = BoxLayout(orientation="vertical", size_hint_y=None, height=50, spacing=3)
        title_area.add_widget(Label(
            text=f"{today.year}年{today.month}月{today.day}日 {weekday}",
            font_size=FONT_TITLE, halign="center", valign="middle",
            color=COLOR_TEXT, bold=True
        ))
        self.work_status_btn = TextButton(
            text="上班中",
            font_size=FONT_CAPTION,
            size_hint_y=None,
            height=20,
            text_color=COLOR_TEXT_LIGHT,
            halign="center"
        )
        self.work_status_btn.bind(on_release=self.toggle_work_status)
        title_area.add_widget(self.work_status_btn)
        root.add_widget(title_area)

        # 功能按钮行
        action_row = BoxLayout(orientation="horizontal", size_hint_y=None, height=30, spacing=SPACING_MD)
        buttons = [
            ("提醒", self.show_remind),
            ("历史", self.go_history),
            ("筛选", self.open_filter_popup),
            ("导出", self.export_tasks),
            ("全完成", self.batch_complete),
        ]
        for text, func in buttons:
            btn = TextButton(text=text, font_size=FONT_CAPTION, size_hint_x=None, width=45, text_color=COLOR_TEXT_GRAY)
            btn.bind(on_press=func)
            action_row.add_widget(btn)
        root.add_widget(action_row)

        # 搜索框
        search_row = BoxLayout(orientation="horizontal", size_hint_y=None, height=40, spacing=5)
        search_input_container = BoxLayout(size_hint_x=1, padding=[1, 1])
        with search_input_container.canvas.before:
            Color(*COLOR_INPUT_BG)
            search_input_container.rect = RoundedRectangle(radius=[RADIUS_MD], pos=search_input_container.pos, size=search_input_container.size)
        search_input_container.bind(pos=self.update_rect, size=self.update_rect)
        self.search_input = TextInput(
            hint_text="搜索任务...",
            font_size=FONT_BODY,
            background_color=(1, 1, 1, 0),
            hint_text_color=COLOR_TEXT_LIGHT
        )
        self.search_input.bind(text=self.on_search)
        search_input_container.add_widget(self.search_input)
        search_row.add_widget(search_input_container)

        clear_btn = TextButton(text="清除", font_size=FONT_CAPTION, size_hint_x=None, width=50, text_color=COLOR_TEXT_GRAY)
        clear_btn.bind(on_release=self.clear_search)
        search_row.add_widget(clear_btn)
        root.add_widget(search_row)

        # 统计信息
        self.info = Label(text="", font_size=FONT_SMALL, size_hint_y=None, height=18, halign="right", valign="middle", color=COLOR_TEXT_LIGHT)
        self.info.bind(size=self.info.setter('text_size'))
        root.add_widget(self.info)

        # 任务列表
        list_container = BoxLayout(orientation="vertical", size_hint=(1, 0.48))
        self.scroll = ScrollView(size_hint=(1, 1))
        self.task_box = GridLayout(cols=1, spacing=4, size_hint_y=None, padding=[0, 2, 0, 2])
        self.task_box.bind(minimum_height=self.task_box.setter("height"))
        self.scroll.add_widget(self.task_box)
        list_container.add_widget(self.scroll)
        root.add_widget(list_container)

        # 底部输入区
        input_area = BoxLayout(orientation="horizontal", size_hint_y=None, height=40, spacing=SPACING_SM)
        self.task_input = TextInput(
            hint_text="输入新任务...", font_size=FONT_BODY, hint_text_color=COLOR_TEXT_LIGHT
        )
        self.task_input.bind(on_text_validate=self.add_task)
        input_area.add_widget(self.task_input)

        img_btn = RoundedButton(text="图", font_size=FONT_CAPTION, size_hint_x=None, width=40, bg_color=COLOR_INPUT_BG, text_color=COLOR_TEXT_GRAY, radius=RADIUS_MD)
        img_btn.bind(on_press=self.select_image)
        input_area.add_widget(img_btn)

        add_btn = RoundedButton(text="+", font_size="16sp", size_hint_x=None, width=40, bg_color=COLOR_PRIMARY, text_color=COLOR_CARD, radius=RADIUS_MD)
        add_btn.bind(on_press=self.add_task)
        input_area.add_widget(add_btn)

        root.add_widget(input_area)

        self.add_widget(root)

    def update_rect(self, instance, *args):
        if hasattr(instance, 'rect'):
            instance.rect.pos = instance.pos
            instance.rect.size = instance.size

    def on_enter(self):
        self.refresh()

    # 搜索
    def on_search(self, instance, text):
        self.search_text = text.strip()
        self.refresh()

    def clear_search(self, *args):
        self.search_input.text = ""
        self.search_text = ""
        self.refresh()

    # 上班状态切换
    def toggle_work_status(self, *args):
        current = date.today().isoformat()
        if current != self.app.today:
            self.app.today = current
            if current not in self.app.data:
                self.app.data[current] = []
            save_data(self.app.data)
        self.app.is_working = not getattr(self.app, 'is_working', True)
        if self.app.is_working:
            self.work_status_btn.text = "上班中"
            self.work_status_btn.text_color = COLOR_TEXT_LIGHT
        else:
            self.work_status_btn.text = "已下班"
            self.work_status_btn.text_color = COLOR_TEXT_GRAY
            self.show_report()
        self.refresh()

    # 筛选
    def open_filter_popup(self, *args):
        popup = FilterPopup(
            current_filter=self.current_filter,
            on_select=self.set_filter,
        )
        popup.open()

    def set_filter(self, filter_text):
        self.current_filter = filter_text
        self.refresh()

    # 图片选择
    def select_image(self, *args):
        if platform == "win":
            from tkinter import filedialog, Tk
            root = Tk()
            root.withdraw()
            path = filedialog.askopenfilename(filetypes=[("图片", "*.png *.jpg *.jpeg *.bmp *.gif")])
            root.destroy()
            if path:
                self.current_image_path = path
                self.app.show_toast("图片已选择")
        elif platform == "android":
            intent = Intent(Intent.ACTION_GET_CONTENT)
            intent.setType("image/*")
            intent.addCategory(Intent.CATEGORY_OPENABLE)
            activity.bind(on_activity_result=self.on_activity_result)
            PythonActivity.mActivity.startActivityForResult(intent, 1001)

    def on_activity_result(self, request_code, result_code, data):
        if request_code == 1001 and result_code == -1:
            uri = data.getData()
            if uri:
                try:
                    resolver = PythonActivity.mActivity.getContentResolver()
                    input_stream = resolver.openInputStream(uri)
                    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
                    file_name = f"task_image_{timestamp}.jpg"
                    dest_path = os.path.join(get_image_dir(), file_name)
                    output_stream = FileOutputStream(dest_path)
                    buffer = bytearray(1024)
                    while True:
                        read = input_stream.read(buffer)
                        if read == -1:
                            break
                        output_stream.write(buffer, 0, read)
                    input_stream.close()
                    output_stream.close()
                    self.current_image_path = dest_path
                    self.app.show_toast("图片已选择")
                except Exception as e:
                    self.app.show_toast(f"图片读取失败: {e}")

    # 添加任务
    def add_task(self, *args):
        content = self.task_input.text.strip()
        if not content and not self.current_image_path:
            self.app.show_toast("先输入点内容吧~")
            return
        lines = [l.strip() for l in content.splitlines() if l.strip()]
        if not lines and self.current_image_path:
            img_name = os.path.basename(self.current_image_path)
            if len(img_name) > 20:
                img_name = img_name[:20] + "..."
            lines = [f"图片：{img_name}"]
        elif not lines:
            self.app.show_toast("先输入点内容吧~")
            return
        for line in lines:
            task = {
                "content": line,
                "status": "pending",
                "time": datetime.now().isoformat(),
                "keywords": extract_keywords(line),
                "pinned": False,
                "note": "",
                "remind": None,
                "image": self.current_image_path
            }
            self.app.data[self.app.today].append(task)
        save_data(self.app.data)
        self.task_input.text = ""
        self.current_image_path = None
        self.refresh()
        self.app.show_toast(f"已添加 {len(lines)} 条任务")

    # 刷新列表
    def refresh(self):
        self.task_box.clear_widgets()
        tasks = self.app.data.get(self.app.today, [])
        tasks = sorted(tasks, key=lambda x: (not x.get("pinned", False), x.get("time", "")))

        if self.current_filter == "未完成":
            tasks = [t for t in tasks if t["status"] == "pending"]
        elif self.current_filter == "已完成":
            tasks = [t for t in tasks if t["status"] == "done"]
        elif self.current_filter == "已交接":
            tasks = [t for t in tasks if t["status"] == "handover"]

        if self.search_text:
            tasks = [t for t in tasks if self.search_text.lower() in t["content"].lower()]

        total = len(tasks)
        done = sum(1 for t in tasks if t["status"] == "done")
        handover = sum(1 for t in tasks if t["status"] == "handover")
        pending = total - done - handover
        self.info.text = f"{total}项 | {done}完成 | {handover}交接 | {pending}未完"

        if not tasks:
            empty_box = BoxLayout(orientation="vertical", spacing=10, size_hint_y=None, height=150)
            empty_box.add_widget(Label(text="暂无任务，今天很轻松！", font_size=FONT_BODY, halign="center", color=COLOR_TEXT_LIGHT))
            self.task_box.add_widget(empty_box)
        else:
            for i, t in enumerate(tasks):
                row = TaskRow(
                    content=t["content"],
                    status=t["status"],
                    index=i,
                    callback=self.on_action,
                    has_image=bool(t.get("image")),
                    pinned=t.get("pinned", False)
                )
                self.task_box.add_widget(row)

    # 任务操作回调
    def on_action(self, index, action):
        all_tasks = self.app.data.get(self.app.today, [])
        all_tasks = sorted(all_tasks, key=lambda x: (not x.get("pinned", False), x.get("time", "")))
        filtered_indices = []
        for i, t in enumerate(all_tasks):
            if self.current_filter == "未完成" and t["status"] != "pending":
                continue
            if self.current_filter == "已完成" and t["status"] != "done":
                continue
            if self.current_filter == "已交接" and t["status"] != "handover":
                continue
            if self.search_text and self.search_text.lower() not in t["content"].lower():
                continue
            filtered_indices.append(i)

        if index >= len(filtered_indices):
            return
        real_index = filtered_indices[index]

        if action == "pending":
            all_tasks[real_index]["status"] = "pending"
            save_data(self.app.data)
            self.refresh()
        elif action == "ask_status":
            self.app.selected = real_index
            self.show_status(real_index)
        elif action == "detail":
            self.app.selected = real_index
            self.show_detail(real_index)
        elif action == "pin":
            self.toggle_pin(real_index)
        elif action == "edit":
            self.edit_task(real_index)
        elif action == "delete":
            self.delete_task(real_index)

    # 状态选择
    def show_status(self, index):
        content = BoxLayout(orientation="vertical", spacing=10, padding=[25,25,25,25])
        content.add_widget(Label(text="选择状态：", font_size=FONT_BODY, halign="center", color=COLOR_TEXT))
        row = BoxLayout(orientation="horizontal", size_hint_y=None, height=32, spacing=6)
        b1 = RoundedButton(text="完成", bg_color=COLOR_SUCCESS, font_size="12sp")
        b1.bind(on_press=lambda x: self.set_status(index, "done"))
        b2 = RoundedButton(text="交接", bg_color=COLOR_PRIMARY, font_size="12sp")
        b2.bind(on_press=lambda x: self.set_status(index, "handover"))
        b3 = RoundedButton(text="未完成", bg_color=COLOR_TEXT_GRAY, font_size="12sp")
        b3.bind(on_press=lambda x: self.set_status(index, "pending"))
        row.add_widget(b1)
        row.add_widget(b2)
        row.add_widget(b3)
        content.add_widget(row)
        popup = BasePopup(title_text="修改状态", content_widget=content)
        popup.height = dp(200)
        popup.open()
        self.status_popup = popup

    def set_status(self, index, status):
        tasks = self.app.data.get(self.app.today, [])
        if index < len(tasks):
            tasks[index]["status"] = status
            save_data(self.app.data)
            self.refresh()
        if hasattr(self, 'status_popup'):
            self.status_popup.dismiss()

    # 任务详情
    def show_detail(self, index):
        tasks = self.app.data.get(self.app.today, [])
        if index >= len(tasks):
            return
        task = tasks[index]
        status_text = {"pending": "未完成", "done": "已完成", "handover": "已交接"}.get(task["status"], "")
        status_color = COLOR_SUCCESS if task["status"] == "done" else (COLOR_PRIMARY if task["status"] == "handover" else COLOR_TEXT_GRAY)

        popup = Popup(
            title="",
            size_hint=(0.85, 0.8),
            auto_dismiss=False,
            background="",
            background_color=COLOR_BG,
            separator_color=COLOR_LINE
        )

        main_layout = BoxLayout(orientation="vertical", padding=[20, 20, 20, 20], spacing=15)

        top_bar = FloatLayout(size_hint_y=None, height=40)
        title_label = Label(
            text="任务详情",
            font_size="20sp",
            bold=True,
            color=COLOR_TEXT,
            halign="center",
            valign="middle",
            pos_hint={'center_x': 0.5, 'center_y': 0.5}
        )
        close_btn = TextButton(text="关闭", font_size="14sp", size_hint=(None, None), size=(50, 30),
                               text_color=COLOR_TEXT_GRAY, pos_hint={'right': 1, 'top': 1})
        close_btn.bind(on_release=popup.dismiss)
        top_bar.add_widget(title_label)
        top_bar.add_widget(close_btn)
        main_layout.add_widget(top_bar)

        content_width = min(500, Window.width * 0.7)
        content_box = BoxLayout(orientation="vertical", size_hint=(None, 1), width=content_width,
                                pos_hint={'center_x': 0.5})

        scroll = ScrollView(size_hint=(1, 1))
        text_label = Label(
            text=task["content"],
            font_size="16sp",
            color=COLOR_TEXT,
            halign="left",
            valign="top",
            text_size=(content_width, None),
            size_hint_y=None
        )
        text_label.bind(width=lambda instance, value: setattr(instance, 'text_size', (value, None)))
        text_label.bind(texture_size=lambda instance, value: setattr(instance, 'height', value[1]))
        scroll.add_widget(text_label)
        content_box.add_widget(scroll)

        if task.get("image") and os.path.exists(task["image"]):
            img_container = BoxLayout(size_hint_y=None, height=150)
            img = Image(source=task["image"], allow_stretch=True, keep_ratio=True)
            img_container.add_widget(img)
            img_container.bind(on_touch_down=lambda instance, touch: self.open_full_image(task["image"]) if instance.collide_point(*touch.pos) else None)
            content_box.add_widget(img_container)

        main_layout.add_widget(content_box)

        meta_box = BoxLayout(orientation="vertical", size_hint=(None, None), width=content_width,
                             height=70, pos_hint={'center_x': 0.5}, padding=[10, 10], spacing=5)
        def update_meta_rect(instance, *args):
            instance.canvas.before.clear()
            with instance.canvas.before:
                Color(0.95, 0.95, 0.95, 1)
                RoundedRectangle(pos=instance.pos, size=instance.size, radius=[8])
        meta_box.bind(pos=update_meta_rect, size=update_meta_rect)

        meta_box.add_widget(Label(
            text=f"关键词：{task.get('keywords', '')}",
            font_size=FONT_CAPTION,
            color=COLOR_TEXT_GRAY,
            halign="left",
            valign="middle",
            text_size=(content_width - 20, None)
        ))
        meta_box.add_widget(Label(
            text=f"状态：{status_text}",
            font_size=FONT_BODY,
            color=status_color,
            halign="left",
            valign="middle",
            bold=True,
            text_size=(content_width - 20, None)
        ))
        main_layout.add_widget(meta_box)

        popup.content = main_layout
        popup.open()
        self.detail_popup = popup

    def open_full_image(self, image_path):
        content = BoxLayout(orientation="vertical", spacing=10, padding=10)
        img = Image(source=image_path, allow_stretch=True, keep_ratio=True)
        content.add_widget(img)
        close_btn = RoundedButton(text="关闭", bg_color=COLOR_INPUT_BG, text_color=COLOR_TEXT,
                                  size_hint_y=None, height=30)
        popup = Popup(title="查看图片", content=content, size_hint=(0.9, 0.9))
        close_btn.bind(on_release=popup.dismiss)
        content.add_widget(close_btn)
        popup.open()
        self.full_img_popup = popup

    # 置顶
    def toggle_pin(self, index):
        tasks = self.app.data.get(self.app.today, [])
        if index < len(tasks):
            tasks[index]["pinned"] = not tasks[index].get("pinned", False)
            save_data(self.app.data)
            self.refresh()

    # 备注
    def add_note(self, index):
        tasks = self.app.data.get(self.app.today, [])
        if index >= len(tasks):
            return
        content = BoxLayout(orientation="vertical", spacing=10, padding=[25,25,25,25])
        note_input = TextInput(text=tasks[index].get("note", ""), hint_text="输入备注...", font_size=FONT_BODY)
        content.add_widget(note_input)
        popup = BasePopup(title_text="添加备注", content_widget=content, buttons=[("保存", COLOR_PRIMARY, lambda x: self.save_note(index, note_input.text))])
        popup.height = dp(200)
        popup.open()
        self.note_popup = popup

    def save_note(self, index, note):
        tasks = self.app.data.get(self.app.today, [])
        if index < len(tasks):
            tasks[index]["note"] = note
            save_data(self.app.data)
        if hasattr(self, 'note_popup'):
            self.note_popup.dismiss()

    # 编辑任务
    def edit_task(self, index):
        tasks = self.app.data.get(self.app.today, [])
        if index >= len(tasks):
            return
        content = BoxLayout(orientation="vertical", spacing=10, padding=[25,25,25,25])
        edit_input = TextInput(text=tasks[index]["content"], font_size=FONT_BODY)
        content.add_widget(edit_input)

        def save_callback(instance):
            new_text = edit_input.text.strip()
            if new_text:
                tasks[index]["content"] = new_text
                tasks[index]["keywords"] = extract_keywords(new_text)
                save_data(self.app.data)
                self.refresh()
                if hasattr(self, 'edit_popup'):
                    self.edit_popup.dismiss()
            else:
                self.app.show_toast("内容不能为空")

        save_btn = RoundedButton(text="保存", bg_color=COLOR_PRIMARY, size_hint_y=None, height=30)
        save_btn.bind(on_press=save_callback)
        content.add_widget(save_btn)

        popup = BasePopup(title_text="编辑任务", content_widget=content)
        popup.height = dp(200)
        popup.open()
        self.edit_popup = popup

    # 删除任务
    def delete_task(self, index):
        tasks = self.app.data.get(self.app.today, [])
        if index < len(tasks):
            del tasks[index]
            save_data(self.app.data)
            self.refresh()

    # 任务单独提醒
    def set_task_remind(self, index):
        tasks = self.app.data.get(self.app.today, [])
        if index >= len(tasks):
            return
        content = BoxLayout(orientation="vertical", spacing=10, padding=[25,25,25,25])
        content.add_widget(Label(text="设置提醒时间（格式 HH:MM）", font_size=FONT_BODY, halign="center", color=COLOR_TEXT))
        remind_input = TextInput(text=tasks[index].get("remind", ""), hint_text="例如 15:30", font_size=FONT_BODY)
        content.add_widget(remind_input)
        popup = BasePopup(title_text="任务提醒", content_widget=content, buttons=[("保存", COLOR_PRIMARY, lambda x: self.save_task_remind(index, remind_input.text))])
        popup.height = dp(200)
        popup.open()
        self.remind_task_popup = popup

    def save_task_remind(self, index, remind_text):
        tasks = self.app.data.get(self.app.today, [])
        if index < len(tasks):
            if re.match(r'^([01]?[0-9]|2[0-3]):[0-5][0-9]$', remind_text.strip()):
                tasks[index]["remind"] = remind_text.strip()
                save_data(self.app.data)
                if hasattr(self, 'remind_task_popup'):
                    self.remind_task_popup.dismiss()
                self.app.show_toast("任务提醒已设置")
            else:
                self.app.show_toast("时间格式错误，请用 HH:MM")

    # 备份与恢复
    def backup_data(self, *args):
        try:
            with open(get_backup_path(), "w", encoding="utf-8") as f:
                json.dump(self.app.data, f, ensure_ascii=False, indent=2)
            self.app.show_toast("备份成功")
        except Exception as e:
            self.app.show_toast(f"备份失败: {e}")

    def restore_data(self, *args):
        try:
            if os.path.exists(get_backup_path()):
                with open(get_backup_path(), "r", encoding="utf-8") as f:
                    self.app.data = json.load(f)
                save_data(self.app.data)
                self.refresh()
                self.app.show_toast("恢复成功")
            else:
                self.app.show_toast("没有备份文件")
        except Exception as e:
            self.app.show_toast(f"恢复失败: {e}")

    # 每日报告
    def show_report(self):
        tasks = self.app.data.get(self.app.today, [])
        total = len(tasks); done = sum(1 for t in tasks if t["status"]=="done"); handover = sum(1 for t in tasks if t["status"]=="handover"); pending = total-done-handover
        rate = (done/total*100) if total>0 else 0
        content = BoxLayout(orientation="vertical", spacing=8, padding=[25,25,25,25])
        content.add_widget(Label(
            text=f"总计：{total} 项\n已完成：{done} 项\n已交接：{handover} 项\n未完成：{pending} 项\n\n完成率：{rate:.1f}%",
            font_size=FONT_BODY, halign="center", color=COLOR_TEXT
        ))
        popup = BasePopup(title_text="每日报告", content_widget=content, buttons=[("关闭", COLOR_INPUT_BG, self.dismiss_report)])
        popup.height = dp(280)
        popup.open()
        self.report_popup = popup

    def dismiss_report(self, *args):
        if hasattr(self, 'report_popup'):
            self.report_popup.dismiss()

    # 批量操作
    def batch_complete(self, *args):
        for t in self.app.data.get(self.app.today, []):
            t["status"] = "done"
        save_data(self.app.data)
        self.refresh()
        self.app.show_toast("全部搞定！")

    def export_tasks(self, *args):
        tasks = self.app.data.get(self.app.today, [])
        if not tasks:
            self.app.show_toast("没有任务可以导出~")
            return
        lines = [f"任务清单 - {self.app.today}", ""]
        for i, t in enumerate(tasks, 1):
            s = {"pending": "未完成", "done": "已完成", "handover": "已交接"}.get(t["status"], "")
            lines.append(f"{i}. [{s}] {t['content']}")
        path = f"tasks_{self.app.today}.txt"
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write("\n".join(lines))
            self.app.show_toast(f"导出成功：{path}")
        except Exception as e:
            self.app.show_toast(f"导出失败: {e}")

    # 全局提醒设置
    def show_remind(self, *args):
        content = BoxLayout(orientation="vertical", spacing=15)
        content.add_widget(Label(
            text="设置提醒时间（前5分钟通知）",
            color=COLOR_TEXT_GRAY, font_size="14sp",
            halign="left", text_size=(None, None),
            size_hint_y=None, height=20
        ))
        time_row = BoxLayout(orientation="horizontal", spacing=10, size_hint_y=None, height=48)
        self.h_input = TextInput(
            text=str(getattr(self.app, 'remind_hour', 18)), hint_text="时",
            font_size=FONT_BODY, input_filter="int", size_hint_x=0.4, height=48
        )
        time_row.add_widget(self.h_input)
        colon_label = Label(
            text=":", font_size="24sp", bold=True, color=COLOR_TEXT,
            size_hint_x=None, width=30, valign="middle"
        )
        colon_label.bind(size=colon_label.setter('text_size'))
        time_row.add_widget(colon_label)
        self.m_input = TextInput(
            text=str(getattr(self.app, 'remind_minute', 0)), hint_text="分",
            font_size=FONT_BODY, input_filter="int", size_hint_x=0.4, height=48
        )
        time_row.add_widget(self.m_input)
        content.add_widget(time_row)

        buttons = [
            ("取消", COLOR_INPUT_BG, self.dismiss_remind),
            ("保存", COLOR_PRIMARY, self.save_remind)
        ]
        popup = BasePopup(title_text="提醒设置", content_widget=content, buttons=buttons)
        popup.height = dp(250)
        popup.open()
        self.remind_popup = popup

    def dismiss_remind(self, *args):
        if hasattr(self, 'remind_popup'):
            self.remind_popup.dismiss()

    def save_remind(self, *args):
        try:
            h = int(self.h_input.text) if self.h_input.text else 18
            m = int(self.m_input.text) if self.m_input.text else 0
            if 0 <= h <= 23 and 0 <= m <= 59:
                self.app.remind_hour = h
                self.app.remind_minute = m
                self.dismiss_remind()
                self.app.show_toast(f"好哒！{h:02d}:{m:02d}前5分钟提醒你~")
            else:
                self.app.show_toast("请输入有效时间哦~")
        except:
            self.app.show_toast("请输入有效时间哦~")

    def go_history(self, *args):
        self.manager.current = "history"

    def go_today(self, *args):
        self.manager.current = "main"

# ========== 历史页面 ==========
class HistoryScreen(Screen):
    def __init__(self, app, **kwargs):
        super().__init__(**kwargs)
        self.app = app
        self.build_ui()

    def build_ui(self):
        root = BoxLayout(orientation="vertical", padding=[SPACING_XL, 16], spacing=5)
        header = BoxLayout(orientation="horizontal", size_hint_y=None, height=36, spacing=10)
        header.add_widget(Label(text="历史记录", font_size=FONT_TITLE, halign="left", color=COLOR_TEXT, bold=True, size_hint_x=0.5))

        backup_btn = TextButton(text="备份", font_size=FONT_CAPTION, size_hint_x=None, width=40, text_color=COLOR_TEXT_GRAY)
        backup_btn.bind(on_release=self.app.main_screen.backup_data)
        header.add_widget(backup_btn)
        restore_btn = TextButton(text="恢复", font_size=FONT_CAPTION, size_hint_x=None, width=40, text_color=COLOR_TEXT_GRAY)
        restore_btn.bind(on_release=self.app.main_screen.restore_data)
        header.add_widget(restore_btn)

        today_btn = TextButton(text="今天", font_size=FONT_CAPTION, size_hint_x=None, width=40, text_color=COLOR_PRIMARY, bold=True)
        today_btn.bind(on_press=self.go_back)
        header.add_widget(today_btn)
        root.add_widget(header)

        self.scroll = ScrollView(size_hint=(1, 0.9))
        self.hist_box = GridLayout(cols=1, spacing=4, size_hint_y=None, padding=1)
        self.hist_box.bind(minimum_height=self.hist_box.setter("height"))
        self.scroll.add_widget(self.hist_box)
        root.add_widget(self.scroll)

        back_btn = TextButton(text="返回今天", font_size=FONT_CAPTION, size_hint_y=None, height=30, text_color=COLOR_PRIMARY)
        back_btn.bind(on_press=self.go_back)
        root.add_widget(back_btn)

        self.add_widget(root)

    def update_rect(self, instance, *args):
        if hasattr(instance, 'rect'):
            instance.rect.pos = instance.pos
            instance.rect.size = instance.size

    def on_enter(self):
        self.refresh()

    def refresh(self):
        self.hist_box.clear_widgets()
        dates = sorted([d for d in self.app.data.keys() if d != self.app.today], reverse=True)

        if not dates:
            self.hist_box.add_widget(Label(text="暂无历史记录", font_size=FONT_BODY, color=COLOR_TEXT_LIGHT, size_hint_y=None, height=40))

        for date_str in dates:
            tasks = self.app.data[date_str]
            done = sum(1 for t in tasks if t["status"] == "done")
            handover = sum(1 for t in tasks if t["status"] == "handover")
            pending = sum(1 for t in tasks if t["status"] == "pending")

            card = RoundedButton(
                text=f"{date_str}   {done}完成 {handover}交接 {pending}未完",
                font_size=FONT_CAPTION,
                size_hint_y=None,
                height=38,
                bg_color=COLOR_CARD,
                text_color=COLOR_TEXT,
                halign="left",
                padding=[12, 0]
            )
            card.bind(on_press=lambda x, d=date_str: self.toggle_detail(d))
            self.hist_box.add_widget(card)

    def toggle_detail(self, date_str):
        for child in self.hist_box.children:
            if hasattr(child, 'date_key') and child.date_key == date_str:
                self.hist_box.remove_widget(child)
                return

        tasks = self.app.data.get(date_str, [])
        detail = GridLayout(cols=1, spacing=2, size_hint_y=None, padding=[20, 5, 10, 5])
        detail.bind(minimum_height=detail.setter("height"))
        detail.date_key = date_str

        for task in tasks:
            status = task["status"]
            if status == "done":
                prefix = "[完成]"
            elif status == "handover":
                prefix = "[交接]"
            else:
                prefix = "[未完]"

            row = BoxLayout(orientation="horizontal", size_hint_y=None, height=26, spacing=5)
            row.add_widget(Label(text=prefix, font_size=FONT_SMALL, size_hint_x=None, width=45, color=COLOR_TEXT_LIGHT))
            row.add_widget(Label(text=task["content"], font_size=FONT_CAPTION, halign="left", color=COLOR_TEXT))
            detail.add_widget(row)

        self.hist_box.add_widget(detail)

    def go_history(self, *args):
        self.manager.current = "history"

    def go_back(self, *args):
        self.manager.current = "main"

# ========== 主程序 ==========
class TaskApp(App):
    def build(self):
        self.data = load_data()
        self.today = date.today().isoformat()
        if self.today not in self.data:
            self.data[self.today] = []
        self.is_working = True
        self.remind_hour = 18
        self.remind_minute = 0
        self.last_remind = None

        Window.clearcolor = COLOR_BG

        self.sm = ScreenManager()
        self.main_screen = MainScreen(self, name="main")
        self.history_screen = HistoryScreen(self, name="history")
        self.sm.add_widget(self.main_screen)
        self.sm.add_widget(self.history_screen)

        Clock.schedule_interval(self.check_remind, 30)

        return self.sm

    def show_toast(self, msg):
        if platform == "android":
            try:
                from android.widget import Toast
                Toast.makeText(PythonActivity.mActivity, msg, Toast.LENGTH_SHORT).show()
            except:
                pass
        else:
            print(f"提示：{msg}")

    def check_remind(self, dt):
        now = datetime.now()
        if self.is_working:
            remind = now.replace(hour=self.remind_hour, minute=self.remind_minute, second=0, microsecond=0)
            before = remind - timedelta(minutes=5)
            if now.hour == before.hour and now.minute == before.minute:
                if self.last_remind != now.date().isoformat():
                    self.last_remind = now.date().isoformat()
                    tasks = self.data.get(self.today, [])
                    pending = sum(1 for t in tasks if t["status"] == "pending")
                    handover = sum(1 for t in tasks if t["status"] == "handover")
                    if pending > 0 or handover > 0:
                        msg = f"还有{pending}项未完成，{handover}项未交接，抓紧啦！"
                    else:
                        msg = "太棒了！任务已全部完成！"
                    self.notify(msg)

        current_time = now.strftime("%H:%M")
        for date_str, tasks in self.data.items():
            for task in tasks:
                if task.get("remind") == current_time and task.get("status") != "done":
                    msg = f"任务提醒：{task['content']}"
                    self.notify(msg)
                    task["remind"] = None
                    save_data(self.data)

    def notify(self, msg):
        if platform == "android":
            try:
                service = PythonActivity.mActivity.getSystemService(Context.NOTIFICATION_SERVICE)
                builder = NotificationBuilder(PythonActivity.mActivity)
                builder.setContentTitle("任务清单提醒")
                builder.setContentText(msg)
                builder.setSmallIcon(PythonActivity.mActivity.getApplicationInfo().icon)
                service.notify(1, builder.build())
            except:
                pass
        else:
            content = BoxLayout(orientation="vertical", spacing=10, padding=[25, 25, 25, 25])
            content.add_widget(Label(text=msg, font_size=FONT_BODY, halign="center", color=COLOR_TEXT))
            popup = Popup(title="任务清单提醒", content=content, size_hint=(0.7, 0.3))
            popup.open()

if __name__ == "__main__":
    TaskApp().run()