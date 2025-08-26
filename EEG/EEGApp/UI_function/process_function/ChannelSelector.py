import tkinter as tk
import mne
from tkinter import messagebox

class ChannelSelector:
    def __init__(self, master, channels):
        self.master = master
        self.channels = channels
        self.selected_channels=[]
        self.var_list = [tk.BooleanVar() for _ in channels] # 用于保存复选框的状态
        self.create_widgets()
        
    def create_widgets(self):
        # 创造复选框
        for i, channel in enumerate(self.channels):
            chk = tk.Checkbutton(self.master, text=channel, variable=self.var_list[i])
            chk.grid(row=i // 8, column=i % 8, sticky='w')

        # 创建全选按钮
        self.select_all_btn = tk.Button(self.master, text="全选", command=self.toggle_select_all)
        self.select_all_btn.grid(row=len(self.channels) // 8 + 1, column=0, columnspan=4)

        # 创建确认按钮
        self.confirm_btn = tk.Button(self.master, text="确认", command=self.confirm_selection)
        self.confirm_btn.grid(row=len(self.channels) // 8 + 1, column=4, columnspan=4)
        # 添加提示文字
        self.warning_label = tk.Label(self.master, text="请删除无用电极:ECG、HEROR、HEOL、VEOU、VEOL", fg="red")  # 这里可以设置文字颜色
        self.warning_label.grid(row=len(self.channels) // 8 + 2, column=0, columnspan=16)  # 设置在按钮下方，并跨越所有列
        
    def toggle_select_all(self):
        # 切换全选与不选
        new_state = not all(var.get() for var in self.var_list)
        # 判断是否已经全选
        for var in self.var_list:
            var.set(new_state)

    def confirm_selection(self):
        # 生成选择的名字列表
        self.selected_channels = [channel for var, channel in zip(self.var_list, self.channels) if var.get()]
        messagebox.showinfo("选择的通道", f"您选择的通道: {', '.join(self.selected_channels)}")
        self.master.quit()
        self.master.destroy() # 关闭窗口
        
def Ch_select(root,raw):
    names = raw.ch_names
    root = tk.Toplevel(root)
    root.title("选择通道")
    app = ChannelSelector(root, names)
    root.mainloop()
    raw_selected=raw.copy().pick(app.selected_channels)
    return raw_selected