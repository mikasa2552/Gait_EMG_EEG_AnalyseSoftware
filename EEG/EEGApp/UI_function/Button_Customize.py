import tkinter as tk

class Button_Customize(tk.Button):
    '''改变按钮颜色'''
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        self.default_color = kwargs.get('bg', 'lightblue')
        self.hover_color = kwargs.get('hover_color', '#B6D0E2')
        
        # 绑定鼠标事件
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)

    def on_enter(self, event):
        # 鼠标悬停时改变按钮颜色
        self.config(bg=self.hover_color)

    def on_leave(self, event):
        # 鼠标离开时恢复按钮颜色
        self.config(bg=self.default_color)