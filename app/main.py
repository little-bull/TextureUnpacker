import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
from tkinter import ttk
from threading import Timer
from PIL import Image, ImageTk
import os
import plistlib
import plistutils
from tkinterdnd2 import TkinterDnD, DND_FILES
from pathlib import Path


class TextureUnpackerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("TextureUnpacker")
        self.initWindow()

        self.initLeftFrame()
        self.initRightFrame()


    def initWindow(self):
        # 设置窗口宽度为屏幕的 2/3，高度为屏幕的 2/3，并居中显示
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        window_width = (2 * screen_width) // 3
        window_height = (2 * screen_height) // 3
        x_pos = (screen_width - window_width) // 2
        y_pos = (screen_height - window_height) // 2
        self.root.geometry(f"{window_width}x{window_height}+{x_pos}+{y_pos}")
        self.root.resizable(False, False)  # 固定窗口大小

        # 创建框架来分隔左侧（拖拽区域）和右侧（.plist 文件列表）
        self.main_frame = tk.Frame(root)
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)

    def initLeftFrame(self):
        self.plist_path = None
        self.image_path = None
        # 左侧（拖拽区域）
        self.left_frame = tk.Frame(self.main_frame)
        self.left_frame.pack(side="left", fill="both", expand=True)

        # Plist 行
        self.plist_frame = tk.Frame(self.left_frame)
        self.plist_frame.pack(pady=10, fill="x")
        self.plist_label = tk.Label(self.plist_frame, text="Plist:", width=8, anchor="w")
        self.plist_label.pack(side="left")
        self.plist_entry = tk.Entry(self.plist_frame, width=50, state="disabled")
        self.plist_entry.pack(side="left", fill="x", expand=True)

        # Texture 行
        self.texture_frame = tk.Frame(self.left_frame)
        self.texture_frame.pack(pady=10, fill="x")
        self.texture_label = tk.Label(self.texture_frame, text="Texture:", width=8, anchor="w")
        self.texture_label.pack(side="left")
        self.texture_entry = tk.Entry(self.texture_frame, width=50, state="disabled")
        self.texture_entry.pack(side="left", fill="x", expand=True)

        # Drop Area
        self.drop_area = tk.Label(self.left_frame, text="Drop a plist here or select one.",
                                  bg="lightgray", fg="yellow", font=("Arial", 20, "bold"),
                                  width=40, height=10, relief="ridge")
        self.drop_area.pack(pady=20, fill="both", expand=True)


        # Buttons
        self.button_frame = tk.Frame(self.left_frame)
        self.button_frame.pack(pady=10)

        self.clear_btn = tk.Button(self.button_frame, text="Clear", command=self.clear_drop_area)
        self.clear_btn.pack(side="left", padx=5)

        self.convert_jpg_btn = tk.Button(self.button_frame, text="JPG", command=self.convert_to_jpg)
        self.convert_jpg_btn.pack(side="left", padx=5)

        self.convert_png_btn = tk.Button(self.button_frame, text="PNG", command=self.convert_to_png)
        self.convert_png_btn.pack(side="left", padx=5)
        self.set_convert_button(False)

        # Variables to hold state
        self.image_displayed = None
        self.image_path = None

        # Initialize event bindings
        self.drop_area.bind("<Button-1>", self.select_files)  # Bind the click event for file selection
        self.drop_area.drop_target_register(DND_FILES)  # 注册拖拽区域接收文件
        self.drop_area.dnd_bind('<<Drop>>', self.on_drop)  # 绑定文件放下事件


    def initRightFrame(self):
        # icon图标
        self.split_images = []
        # 右侧（.plist 文件列表）
        self.right_frame = tk.Frame(self.main_frame)
        self.right_frame.pack(side="right", fill="y")

        # 创建 Treeview
        self.plist_treeview = ttk.Treeview(self.right_frame, columns=("name",))
        self.plist_treeview.heading("#0", text="Img")
        self.plist_treeview.column("#0", anchor="w", width=50)
        self.plist_treeview.heading("#1", text="Name")
        self.plist_treeview.column("#1", anchor="w", width=200)
        self.plist_treeview.pack(side="left", fill="both", expand=True)

        # 添加滚动条
        self.scrollbar = tk.Scrollbar(self.right_frame, orient="vertical", command=self.plist_treeview.yview)
        self.scrollbar.pack(side="right", fill="y")
        self.plist_treeview.config(yscrollcommand=self.scrollbar.set)

        # 绑定双击事件以启用编辑功能
        # self.plist_treeview.bind("<Double-1>", self.on_item_double_click)

    def on_item_double_click(self, event):
        # 获取双击的项
        item = self.plist_treeview.identify('item', event.x, event.y)

        # 获取当前的值
        old_value = self.plist_treeview.item(item, "values")[0]

        # 创建一个弹出窗口
        self.edit_dialog(item, old_value)

    def edit_dialog(self, item, old_value):
        # 创建一个新的窗口
        dialog = tk.Toplevel(self.root)
        dialog.title("Edit Item")

        # 创建标签
        label = tk.Label(dialog, text="Edit Name:")
        label.pack(padx=10, pady=5)

        # 创建输入框并设置初始值
        entry = tk.Entry(dialog)
        entry.insert(0, old_value)
        entry.pack(padx=10, pady=5)

        # 创建确认按钮
        def confirm():
            new_value = entry.get()
            self.plist_treeview.item(item, values=(new_value,))
            dialog.destroy()

        # 创建取消按钮
        def cancel():
            dialog.destroy()

        # 确认按钮
        confirm_button = tk.Button(dialog, text="Confirm", command=confirm)
        confirm_button.pack(side="left", padx=10, pady=5)

        # 取消按钮
        cancel_button = tk.Button(dialog, text="Cancel", command=cancel)
        cancel_button.pack(side="right", padx=10, pady=5)

        # 绑定回车键（Enter）到确认按钮
        dialog.bind("<Return>", lambda event: confirm())

        # 绑定关闭窗口时的操作
        dialog.protocol("WM_DELETE_WINDOW", cancel)

    def set_convert_button(self, enable):
        if enable:
           self.convert_jpg_btn.config(state="normal", bg="#007AFF")
           self.convert_png_btn.config(state="normal", bg="#007AFF")
        else:
            self.convert_jpg_btn.config(state="disabled", bg="#B0B0B0")
            self.convert_png_btn.config(state="disabled", bg="#B0B0B0")

    def select_files(self, event=None):
        """Handle selecting files."""
        plist_file = filedialog.askopenfilename(title="Select a .plist file",
                                                filetypes=(("Plist files", "*.plist"),))
        if plist_file:
            self.handle_plist_file(plist_file)

    def handle_plist_file(self, plist_file):
        """Handle the plist file after selection."""
        # Set plist file to the entry (read-only)
        self.plist_entry.config(state="normal")
        self.plist_entry.delete(0, tk.END)
        self.plist_entry.insert(0, plist_file)
        self.plist_entry.config(state="disabled")
        self.plist_path = plist_file
        self.image_path = None

        # Check for a same-name .png file
        png_file = plist_file.rsplit(".", 1)[0] + ".png"
        if os.path.exists(png_file):
            self.image_path = png_file
            self.texture_entry.config(state="normal")
            self.texture_entry.delete(0, tk.END)
            self.texture_entry.insert(0, png_file)
            self.texture_entry.config(state="disabled")
            self.display_image(png_file)
            self.set_convert_button(True)
        else:
            self.show_status("No matching .png file found!")
            self.texture_entry.config(state="normal")
            self.texture_entry.delete(0, tk.END)
            self.texture_entry.config(state="disabled")
            self.clear_drop_area()
            self.set_convert_button(False)


        # Update the Plist listbox
        self.update_plist_listbox(plist_file)

    def on_drop(self, event):
        """Handle the drop event."""
        file_path = event.data
        if file_path.endswith(".plist"):
            self.handle_plist_file(file_path)

    def update_plist_listbox(self, plist_file):
        self.split_images = []

        """更新 Plist 列表框"""
        with open(plist_file, 'rb') as f:
            plist = plistlib.load(f)

        items = plistutils.check_format(plist)

        # 清空 Treeview 内容
        for item in self.plist_treeview.get_children():
            self.plist_treeview.delete(item)

        # 加载纹理图像
        png_file = plist_file.rsplit(".", 1)[0] + ".png"
        if os.path.exists(png_file):
            texture_image = Image.open(png_file)
        else:
            self.show_status("No matching .png file found!")
            return
            
        # 遍历所有子项并添加到 Treeview
        for item in items:
            icon_image = plistutils.extract_image(texture_image, item)
            icon_image.thumbnail((20, 20), Image.Resampling.LANCZOS)
            icon_image = ImageTk.PhotoImage(icon_image)


            # 在 Treeview 中插入数据并显示图像
            vlaues = ( item['pathname'] ,)
            item_id = self.plist_treeview.insert("", tk.END,image = icon_image, values=vlaues)
            self.split_images.append((icon_image,item))



    def display_image(self, image_path):
        """Display an image in the drop area."""
        image = Image.open(image_path)

        # Resize image to fit the drop area
        drop_area_width = self.drop_area.winfo_width()
        drop_area_height = self.drop_area.winfo_height()

        # Scale image while maintaining aspect ratio
        image.thumbnail((drop_area_width, drop_area_height), Image.Resampling.LANCZOS)

        self.image_displayed = ImageTk.PhotoImage(image)
        self.drop_area.config(image=self.image_displayed, text="")
        self.drop_area.unbind("<Button-1>")  # Disable clicking on the drop area

    def clear_drop_area(self):
        """Clear the drop area and restore its functionality."""
        self.image_displayed = None  # 清除对图片的引用，防止异常
        self.drop_area.config(image="", text="Drop a plist here or select one.")  # 设置空字符串代替 None
        self.drop_area.bind("<Button-1>", self.select_files)  # 重新绑定拖拽区域
        # 获取所有根节点的ID
        for item in self.plist_treeview.get_children():
            self.plist_treeview.delete(item)
        self.split_images = []

        self.plist_entry.config(state="normal")
        self.plist_entry.delete(0, tk.END)
        self.plist_entry.insert(0, "")
        self.plist_entry.config(state="disabled")

        self.texture_entry.config(state="normal")
        self.texture_entry.delete(0, tk.END)
        self.texture_entry.insert(0, "")
        self.texture_entry.config(state="disabled")



    def showTip(self, message, title = "waring"):
        """在屏幕中央显示一个美观的提示对话框，3秒后自动消失"""
        # 创建顶层窗口
        tip_window = tk.Toplevel(self.root)
        tip_window.overrideredirect(True)  # 去掉标题栏
        tip_window.attributes("-topmost", True)  # 窗口置顶
        tip_window.attributes("-alpha", 0.95)  # 半透明效果
        tip_window.configure(bg="white")  # 背景为白色

        # 添加边框和圆角效果（模拟）
        tip_window.configure(highlightbackground="#A9A9A9", highlightthickness=2)  # 灰色边框

        # 创建标题标签
        title_label = tk.Label(
            tip_window, text=title, font=("Arial", 14, "bold"), bg="white", fg="black", anchor="center"
        )
        title_label.pack(pady=(10, 5), padx=20)

        # 创建内容标签
        message_label = tk.Label(
            tip_window, text=message, font=("Arial", 12), bg="white", fg="black", anchor="center", justify="center"
        )
        message_label.pack(pady=(0, 10), padx=20)

        # 设置窗口大小和位置
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        tip_window.update_idletasks()
        window_width = tip_window.winfo_width()
        window_height = tip_window.winfo_height()
        x_pos = (screen_width - window_width) // 2
        y_pos = (screen_height - window_height) // 2
        tip_window.geometry(f"{window_width}x{window_height}+{x_pos}+{y_pos}")

        # 自动销毁窗口
        def close_tip():
            if tip_window.winfo_exists():
                tip_window.destroy()

        Timer(3, close_tip).start()



    def convert_to_jpg(self):
        if not self.image_path:
            self.showTip("No Png Path")
            return
        if not self.split_images:
            self.showTip("No Png Split Images")
            return

        dir_path = Path(self.image_path).parent
        image = Image.open(self.image_path)
        for _,item in self.split_images:
            plistutils.extract_image_2_jpg(image,str(dir_path),item)

        self.showTip("Convert Split Png Success")

    def convert_to_png(self):
        if not self.image_path:
            self.showTip("No Png Path")
            return
        if not self.split_images:
            self.showTip("No Png Split Images")
            return

        dir_path = Path(self.image_path).parent
        image = Image.open(self.image_path)
        for _,item in self.split_images:
            plistutils.extract_image_2_png(image,str(dir_path),item)

        self.showTip("Convert Split Png Success")

if __name__ == "__main__":
    root = TkinterDnD.Tk()  # 使用 TkinterDnD 代替 tk.Tk()
    app = TextureUnpackerApp(root)
    root.mainloop()