import tkinter as tk
import queue
import threading
import mne
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class ICA:
    def __init__(self, root, n, ica, raw):
        self.__root = root
        self.__n = n
        self.raw_ica = []
        self.__ica = ica
        self.__raw = raw
        self.__check_vars = []

        # 创建一个框架来放置滚动区域和按钮
        self.main_frame = tk.Frame(self.__root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # 创建一个 Canvas 用于滚动
        self.canvas = tk.Canvas(self.main_frame)
        self.scrollable_frame = tk.Frame(self.canvas)

        # 创建一个滚动条
        self.scrollbar = tk.Scrollbar(self.main_frame, orient="vertical", command=self.canvas.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        # 将 Canvas 和 Frame 绑定
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        # 绑定鼠标滚轮事件
        self.canvas.bind_all("<MouseWheel>", self.on_mouse_wheel)

        self.create_canvas_grid()
        self.create_bottom_buttons()

    def on_mouse_wheel(self, event):
        # 鼠标滚轮向上滚动
        if event.delta > 0:
            self.canvas.yview_scroll(-1, "units")  # 向上滚动一单位
        # 鼠标滚轮向下滚动
        elif event.delta < 0:
            self.canvas.yview_scroll(1, "units")  # 向下滚动一单位
            
    def create_canvas_grid(self):
    # 创建绘图区和对应的复选框与按钮
        for i in range(self.__n):
            # 每 8 个 canvas 一行
            if i % 8 == 0:
                row_frame = tk.Frame(self.scrollable_frame)
                row_frame.pack(side=tk.TOP, pady=5)  # 每个行框 vertically stack

            # 创建一个框架来放置 canvas 
            canvas_frame = tk.Frame(row_frame)
            canvas_frame.pack(side=tk.LEFT, padx=5)  # 使得canvas水平排列
            
            # 创建 matplotlib 图形，设置较小的大小
            fig, ax = plt.subplots(figsize=(2, 2), dpi=100)  # 设置图形大小为2x2英寸
            # 隐藏坐标轴
            ax.set_xticks([])  # 隐藏横轴刻度
            ax.set_yticks([])  # 隐藏纵轴刻度
            ax.spines['top'].set_visible(False)  # 隐藏上边框
            ax.spines['right'].set_visible(False)  # 隐藏右边框
            ax.spines['left'].set_visible(False)  # 隐藏左边框
            ax.spines['bottom'].set_visible(False)  # 隐藏下边框

            # 在坐标区域绘制components
            self.__ica.plot_components(picks=i, axes=ax,show=False)

            canvas = FigureCanvasTkAgg(fig, master=canvas_frame)
            canvas.get_tk_widget().pack(side=tk.TOP)

            # 创建一个框架放置复选框和操作按钮
            button_frame = tk.Frame(canvas_frame)  # 新增一个框架放在canvas_frame内部
            button_frame.pack(side=tk.TOP)  # 放在canvas下方

            # 创建复选框
            var = tk.BooleanVar()
            check_button = tk.Checkbutton(button_frame, variable=var)
            check_button.pack(side=tk.LEFT)  # 将复选框放在左侧

            # 创建操作按钮
            action_button = tk.Button(button_frame, text="查看", command=lambda i=i: self.on_action_button_click(i), width=10)
            action_button.pack(side=tk.RIGHT, padx=5,pady=5)  # 将操作按钮放在复选框右侧，并加上适当的间距

            # 将变量存储到列表中
            self.__check_vars.append(var)
        
        # 关闭所有未显示的图形窗口
        plt.close('all')

    def create_bottom_buttons(self):
        # 创建全选和确认按钮，实现固定在底部
        bottom_frame = tk.Frame(self.__root)
        bottom_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=10)
        # 创建左侧框架
        left_frame = tk.Frame(bottom_frame)
        left_frame.pack(side=tk.LEFT, expand=True)  # 左侧框架填充整个高度，并在左边

        # 创建右侧框架
        right_frame = tk.Frame(bottom_frame)
        right_frame.pack(side=tk.RIGHT, expand=True)  # 右侧框架填充整个高度，并在右边

        select_all_button = tk.Button(left_frame, text="全选", command=self.toggle_select_all,width=20, height=2)
        select_all_button.pack(side=tk.TOP,padx=20, pady=5)

        confirm_button = tk.Button(right_frame, text="删除", command=self.confirm_selection,width=20, height=2)
        confirm_button.pack(side=tk.RIGHT ,padx=20, pady=5)
        
    def on_action_button_click(self, index):
        # 创建一个新的窗口来显示成分具体信息
        info_window = tk.Toplevel(self.__root)  # 创建新窗口
        info_window.title(f"成分 {index + 1} 信息")  # 设置窗口标题

        # 创建 matplotlib 图形
        fig = plt.figure(figsize=(8, 6))  # 设置图形大小

        # 使用 GridSpec 创建不规则的子图布局
        gs = gridspec.GridSpec(2, 2)  # 2行2列的网格

        # 第一行左侧占 1/4，右侧占 3/4
        ax1 = fig.add_subplot(gs[0, 0])  # 第一行第一列
        ax2 = fig.add_subplot(gs[0, 1])  # 第一行第二列，后面会细分

        # 将右上角的子图再细分为上下两个
        gs2 = gridspec.GridSpecFromSubplotSpec(2, 1, subplot_spec=gs[0, 1], height_ratios=[3, 1],hspace=0)  # 3/4 和 1/4
        ax3 = fig.add_subplot(gs2[0, 0])  # 右上角的上半部分
        ax4 = fig.add_subplot(gs2[1, 0])  # 右上角的下半部分

        # 第二行左侧占 1/4，右侧占 3/4
        ax5 = fig.add_subplot(gs[1, 0])  # 第二行第一列
        ax6 = fig.add_subplot(gs[1, 1])  # 第二行第二列

        # 将图形嵌入到 Tkinter 窗口
        canvas = FigureCanvasTkAgg(fig, master=info_window)
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # 使用 MNE 的 plot_properties 显示成分信息
        self.__ica.plot_properties(self.__raw, picks=index, axes=[ax1, ax3, ax4, ax5, ax6],show=False)  # 绘制成分属性图

        # 遍历每个子图，隐藏刻度和边框
        for ax in [ax1,ax2]:
            ax.set_xticks([])  # 隐藏横轴刻度
            ax.set_yticks([])  # 隐藏纵轴刻度
            ax.spines['top'].set_visible(False)  # 隐藏上边框
            ax.spines['right'].set_visible(False)  # 隐藏右边框
            ax.spines['left'].set_visible(False)  # 隐藏左边框
            ax.spines['bottom'].set_visible(False)  # 隐藏下边框
        #ax3.set_xticks([])
     
        # 添加关闭按钮
        close_button = tk.Button(info_window, text="关闭", command=info_window.destroy,width=20, height=2)
        close_button.pack(side=tk.BOTTOM, pady=10)
        # 关闭所有未显示的图形窗口
        plt.close('all')


    def toggle_select_all(self):
        # 检查是否所有复选框都被选中
        all_selected = all(var.get() for var in self.__check_vars)

        # 根据当前状态，进行全选或全不选
        for var in self.__check_vars:
            var.set(not all_selected)

    def confirm_selection(self):
        selected_indices = [i for i, var in enumerate(self.__check_vars) if var.get()]
        self.__ica.exclude = selected_indices
        self.raw_ica = self.__raw
        self.__ica.apply(self.raw_ica)
        self.__root.quit()
        self.__root.destroy()

 
def ICA_EEG(root, raw):
    result_queue = queue.Queue()  # 用于存储返回的ICA对象
    raw_ica = None  # 定义一个外部变量来存储app

    def ica_process():
        # 进行ICA计算
        ica = mne.preprocessing.ICA(method='fastica', n_components=0.9999,max_iter='auto')
        ica.fit(raw)
        return ica 

    def run_ica():
        # 在这个函数中进行ICA计算
        result = ica_process()  # 调用长时间运行的函数
        result_queue.put(result)  # 将结果放入队列中

    def show_monitor_window():
        # 创建一个新的监视窗口
        monitor_window = tk.Toplevel(root)
        monitor_window.title("监视窗口")
        label = tk.Label(monitor_window, text="正在进行 ICA 拟合，请稍候...", font=("微软雅黑", 14,'bold'), width=30, fg='#004F98')
        label.pack(padx=20, pady=20)
        return monitor_window

    def check_queue(monitor_window, result_queue):
        nonlocal raw_ica  # 声明使用外部变量
        try:
            result = result_queue.get_nowait()  # 尝试从队列获取ica对象
            monitor_window.quit()
            monitor_window.destroy()  # 关闭监视窗口
            app = use_ica(result)
            raw_ica = app.raw_ica  # 调用处理ica对象的函数
        except queue.Empty:
            # 如果队列为空，继续检查
            root.after(100, lambda: check_queue(monitor_window, result_queue))

    def use_ica(ica):
        n = ica.n_components_  # 获取成分数量
        result_window = tk.Toplevel(root)
        result_window.geometry("1700x800")
        result_window.resizable(False, False)
        result_window.title("选择需要删除的成分")
        
        app = ICA(result_window, n, ica, raw)  # 使用获取的ica对象
        result_window.mainloop()
        return app  # 返回app对象

    def start_ica():
        monitor_window = show_monitor_window()  # 显示监视窗口
        
        # 启动一个新线程来运行长时间运行的函数
        threading.Thread(target=run_ica, daemon=True).start()
        
        # 启动检查队列的循环
        root.after(100, lambda: check_queue(monitor_window, result_queue))

    # 创建监视窗口并启动过程
    start_ica()
    
    # 等待直到app_instance被设置
    while raw_ica is None:
        root.update()  # 更新GUI以响应事件

    return raw_ica  # 返回app对象

# result_dict = {}
# def fit_ica_with_timer(root, raw, method='fastica', max_iter='auto', callback=None):
#     """
#     执行 ICA 拟合，并在 Tkinter 窗口中显示执行状态，拟合完成后自动关闭窗口。

#     参数:
#     raw: 输入的 raw 数据对象。
#     method: ICA 方法，默认为 'fastica'。
#     max_iter: 最多迭代次数，默认为 'auto'。
#     callback: 拟合完成后调用的回调函数，接收拟合后的 ICA 对象。
#     """
#     global ica_result  # 声明全局变量以存储 ICA 对象
#     ica_result = None  # 初始化

#     def fit_ica():
#         """在单独的线程中执行 ICA 拟合。"""
#         global ica_result  # 使用全局变量
#         ica = mne.preprocessing.ICA(method=method, max_iter=max_iter)
#         ica.fit(raw)  # 进行拟合
#         ica_result = ica  # 存储结果
#         # 拟合完成后调用关闭窗口的函数
#         win.after(0, close_window)  # 使用 after() 方法延迟调用

#     def show_message():
#         """显示 Tkinter 窗口并在 ICA 拟合完成后关闭它。"""
#         global win
#         win = tk.Toplevel(root)
#         win.title("ICA 进行中...")

#         # 创建标签
#         label = tk.Label(win, text="正在进行 ICA 拟合，请稍候...", font=("微软雅黑", 14,'bold'),width=30,fg='#004F98')
#         label.pack(padx=20, pady=20)

#         # 启动 ICA 拟合
#         ica_thread = threading.Thread(target=fit_ica)
#         ica_thread.start()

#         # 启动 Tkinter 主事件循环
#         win.protocol("WM_DELETE_WINDOW", close_window)  # 窗口关闭事件
#         win.mainloop()

#     def close_window():
#         """关闭窗口并调用回调函数。"""
#         win.quit()  # 退出主循环
#         win.destroy()  # 销毁窗口
#         if callback is not None:
#             callback(root, ica_result, raw)  # 调用回调函数并传递 ICA 结果

#     # 开始显示窗口
#     show_message()

# # 使用示例
# def handle_ica_result(root, ica, raw):
#     """处理 ICA 结果的回调函数。"""
#     if ica is not None:
#         n = ica.n_components_  # 可以根据需要更改数量
#         new_window = tk.Toplevel(root)
#         new_window.geometry("1700x800")
#         new_window.resizable(False, False)
#         new_window.title("选择需要删除的成分")
        
#         # 这里假设 ICA 是一个类，你需要根据你的实际情况修改
#         app = ICA(new_window, n, ica, raw)
#         new_window.mainloop()  # 启动新的主循环
#         print(111)
#         result_dict['raw_ica'] = app.raw_ica  # 使用全局字典保存结果
#         win.quit()
#         win.destroy()
# def ICA_EEG(root,raw):
#     # 声明一个全局字典来存储结果
#     fit_ica_with_timer(root,raw, callback=handle_ica_result)  # 调用函数执行 ICA 并显示窗口
#     return result_dict.get('raw_ica')