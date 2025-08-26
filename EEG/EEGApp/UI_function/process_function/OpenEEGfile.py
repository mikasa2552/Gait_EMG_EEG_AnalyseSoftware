import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
import mne


def OpenEEGfile():
    # 创建一个隐藏的根窗口
    root = tk.Tk()
    root.withdraw()  # 隐藏根窗口
    
    # 打开文件选择对话框
    file_path = filedialog.askopenfilename(filetypes=[("EEG BDF files", "*.bdf")])
    
    if file_path:
        # 读取文件
        raw = mne.io.read_raw_bdf(file_path, preload=True)
        root.destroy()  # 选择文件后销毁根窗口
        return raw
    else:
        messagebox.showinfo("提示", "请选择正确的文件")
        root.destroy()  # 如果没有选择文件，销毁根窗口