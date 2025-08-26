
import tkinter as tk
from tkinter import ttk, messagebox

# 将100hz的ge事件数据和1000hz的脑电数据事件进行关联
def GE_times_trans(root, Event_dic, Frame_dic, event_names, event_times):
    window = tk.Toplevel(root)
    window.title("Event Marker")
    window.resizable(False, False)

    GE_times_list = []
    GE_list = []
    walk_selected_list = list(Frame_dic.keys())
    walk_selected_list = [int(item) - 1 for item in walk_selected_list]
    unique_events = sorted(list(set(event_names)))

    label = tk.Label(window, width=20, text="选择事件:")
    label.grid(row=0, column=0, columnspan=1, pady=5, padx=10)

    event_var = tk.StringVar()
    event_dropdown = ttk.Combobox(window, textvariable=event_var, width=17)
    event_dropdown['values'] = list(unique_events)
    event_dropdown.grid(row=0, column=1, columnspan=1, pady=5, padx=10)

    def get_index(lst=None, item=''):
        return [index for (index, value) in enumerate(lst) if value == item]

    def epoch_selected():
        start_event = event_var.get()
        start_event_index = get_index(event_names, start_event)
        start_event_index_selected = [start_event_index[pos] for pos in walk_selected_list]
        event_times_selected = [event_times[pos] for pos in start_event_index_selected]
        nonlocal GE_times_list
        for i in range(len(event_times_selected)):
            walk_key = walk_selected_list[i]
            tmp = [item / 100 + float(event_times_selected[i]) for item in Frame_dic[str(walk_key + 1)]]
            GE_times_list.extend(tmp)

    def frame_list():
        nonlocal GE_list
        for key in Event_dic.keys():
            GE_list.extend(Event_dic[key])
        window.quit()  # 退出主事件循环
        window.destroy() # 销毁窗口

    confirm_btn = tk.Button(window, text="确认", width=20, command=lambda: [epoch_selected(), frame_list()])
    confirm_btn.grid(row=1, column=0, columnspan=2, pady=10, padx=10)

    window.protocol("WM_DELETE_WINDOW", window.quit)  # 允许窗口直接关闭

    window.mainloop()  # 启动窗口的主循环

    # 返回数据
    return GE_list, GE_times_list