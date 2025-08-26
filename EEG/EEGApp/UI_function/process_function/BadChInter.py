import matplotlib
matplotlib.use('TkAgg')  # 设置 Matplotlib 使用 TkAgg 后端
import mne
import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# 定义插值函数
def Inter(raw, montage_name):
    easycap_montage = mne.channels.make_standard_montage(montage_name)
    raw.set_montage(easycap_montage)
    if raw.info['bads']:
        raw.interpolate_bads(reset_bads=False)
    #fig = raw.plot_sensors(show_names=True)
    return raw

# 创建 GUI 窗口
def BadChInter(root,raw):
    window = tk.Toplevel(root)
    window.title("选择头型模型")
    
    raw_intered = None
    
    # 下拉列表选项
    montage_options = [
        'standard_1005', 'standard_1020', 'standard_alphabetic', 
        'standard_postfixed', 'standard_prefixed', 'standard_primed', 
        'biosemi16', 'biosemi32', 'biosemi64', 'biosemi128', 
        'biosemi160', 'biosemi256', 'easycap-M1', 'easycap-M10', 
        'easycap-M43', 'EGI_256', 'GSN-HydroCel-32', 
        'GSN-HydroCel-64_1.0', 'GSN-HydroCel-65_1.0', 
        'GSN-HydroCel-128', 'GSN-HydroCel-129', 
        'GSN-HydroCel-256', 'GSN-HydroCel-257', 
        'mgh60', 'mgh70', 'artinis-octamon', 
        'artinis-brite23', 'brainproducts-RNP-BA-128'
    ]
    
    label_choose = tk.Label(window, text='选择所用的头部模型')
    label_choose.grid(row=0, column=0,sticky='e')
    # 创建下拉列表
    selected_montage = tk.StringVar()
    montage_combobox = ttk.Combobox(window, textvariable=selected_montage, values=montage_options, width=50)
    montage_combobox.grid(row=0,column=1, padx=5, pady=5,columnspan=3)
    
    # 设置默认值
    montage_combobox.current(0)

    # 预览按钮
    def preview():
        nonlocal ax
        ax.clear()
        nonlocal raw_intered
        montage_name = selected_montage.get()
        raw_intered=Inter(raw, montage_name)
        raw_intered.plot_sensors(show_names=True, axes=ax,show=False)
        canvas.draw()
        # 关闭所有未显示的图形窗口
        plt.close('all')
        
    def confirm_selection():
        window.quit()
        window.destroy()  # 关闭窗口
        
    fig, ax = plt.subplots()
    # 隐藏坐标轴
    ax.set_xticks([])  # 隐藏横轴刻度
    ax.set_yticks([])  # 隐藏纵轴刻度
    ax.spines['top'].set_visible(False)    # 隐藏上边框
    ax.spines['right'].set_visible(False)  # 隐藏右边框
    ax.spines['left'].set_visible(False)   # 隐藏左边框
    ax.spines['bottom'].set_visible(False)  # 隐藏下边框
    canvas = FigureCanvasTkAgg(fig, master=window)
    canvas.get_tk_widget().grid(row=1, column=0,columnspan=10,sticky='nsew')
    

    preview_button = tk.Button(window, text="预览", command=preview)
    preview_button.grid(row=0, column=4,sticky='nsew',columnspan=2,pady=5)
    
    confirm_button = tk.Button(window, text="确认", command=confirm_selection)
    confirm_button.grid(row=0, column=7,sticky='nsew',columnspan=2,pady=5)

    # 设置行和列的权重以使其自适应窗口大小
    window.grid_rowconfigure(1, weight=1)
    for i in range(10):
        window.grid_columnconfigure(i, weight=1)
    
    window.mainloop()
    
    return raw_intered
