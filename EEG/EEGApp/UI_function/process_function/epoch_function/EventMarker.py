import tkinter as tk
from tkinter import messagebox


# 创建窗口
def EventMarker(root,event_names):
    window = tk.Toplevel(root)
    window.title("Event Marker")
    
    # 去重
    unique_events = sorted(list(set(event_names)))

    # 配置行和列的权重，以便在窗口缩放时动态调整
    window.columnconfigure(0, weight=1)  # 左侧列
    window.columnconfigure(1, weight=0)  # 中间箭头列
    window.columnconfigure(2, weight=1)  # 右侧输入列

    # 标题
    tk.Label(window, text="Event名称", font=("TimesNewRoman", 9,"bold"),fg="#A52A2A").grid(row=0, column=0, columnspan=1, pady=5, padx=10)
    tk.Label(window, text="整数型数字标记", font=("TimesNewRoman", 9,"bold"),fg="#A52A2A").grid(row=0, column=2, pady=5, padx=10)

    # 存储输入框的值
    entries = {}
    # 字典
    event_dict = {}

    # 创建左侧和右侧的元素
    for i, event in enumerate(unique_events):
        tk.Label(window, text=event, font=("TimesNewRoman", 10)).grid(row=i + 1, column=0, padx=10)  # 左侧事件名

        # 添加箭头
        tk.Label(window, text="→", font=("TimesNewRoman", 25),fg="#0437F2").grid(row=i + 1, column=1, padx=5)  # 箭头居中

        entry = tk.Entry(window, width=15, font=("Arial", 10))
        entry.grid(row=i + 1, column=2, pady=5, padx=10)  
        entries[event] = entry  # 将输入框与事件名称关联

    # 确认按钮功能
    def on_confirm():
        nonlocal event_dict 
        for event, entry in entries.items():
            try:
                value = int(entry.get())  # 读取输入并转换为整数
                event_dict[event] = value
            except ValueError:
                messagebox.showerror("输入错误", f"{event} 的值必须是整数")
                return
        messagebox.showinfo("成功", "标记成功!\n" + str(event_dict))
        window.quit()  # 退出主事件循环
        window.destroy() # 销毁窗口

    # 确认按钮
    confirm_button = tk.Button(window, text="确认", command=on_confirm, font=("TimesNewRoman", 10),width=15)
    confirm_button.grid(row=len(unique_events) + 1, column=0, columnspan=3, pady=20)

    # 配置行的权重，使得输入区域随窗口大小变化
    for i in range(len(unique_events) + 1):
        window.rowconfigure(i, weight=1 if i < len(unique_events) else 0)

    window.mainloop()
    return event_dict