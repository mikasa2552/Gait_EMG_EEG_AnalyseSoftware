import tkinter as tk
from tkinter import ttk, messagebox
import mne
import numpy as np
import copy

# 创建主窗口
class EEGSegmentation:
    def __init__(self, master,raw,events,event_dict):
        self.__master = master
        self.__master.title("EEG Segmentation")

        self.__option_var = tk.StringVar()
        self.__option_var.set("Manual Segmentation")  # 默认选项
        
        self.__raw_data = raw
        self.raw_seg = []
        self.__events = events
        self.__event_dict = event_dict

        self.create_main_window()

    def create_main_window(self):
        label = tk.Label(self.__master, width=60,text="选择分割方式:")
        label.pack(pady=10)

        # 创建选择框
        options = ["手动分割", "自动分割"]
        for option in options:
            rb = tk.Radiobutton(self.__master, text=option, variable=self.__option_var,value=option,activebackground='#ADD8E6')
            rb.pack(anchor="center")

        confirm_btn = tk.Button(self.__master, text="确认", width=20,command=self.open_sub_window)
        confirm_btn.pack(pady=10)

    def open_sub_window(self):
        if self.__option_var.get() == "手动分割":
            self.create_manual_window()
        else:
            self.create_auto_window()
            
#######################################################################################手动分割###########################################################################################

    def create_manual_window(self):
        manual_window = tk.Toplevel(self.__master)
        manual_window.title("手动分割")
        manual_window.geometry("400x200")
        manual_window.resizable(False, False)

        frame_seg_0 = tk.Frame(manual_window)
        frame_seg_0.pack(side=tk.TOP, pady=5)
        frame_seg_1 = tk.Frame(manual_window)
        frame_seg_1.pack(side=tk.TOP, pady=5)
        frame_seg_2 = tk.Frame(manual_window)
        frame_seg_2.pack(side=tk.TOP, pady=5)
        frame_seg_3 = tk.Frame(manual_window)
        frame_seg_3.pack(side=tk.TOP, pady=10)
        # 下拉选择框
        label = tk.Label(frame_seg_0, width=20,text="选择事件:",anchor='w')
        label.pack(pady=5,side=tk.LEFT,fill=tk.X)

        self.event_var = tk.StringVar()
        self.event_dropdown = ttk.Combobox(frame_seg_0, textvariable=self.event_var, width=17)
        self.event_dropdown['values'] = list(self.__event_dict.keys())
        self.event_dropdown.pack(pady=5,side=tk.RIGHT)

        # 输入框
        self.tmin_var = tk.DoubleVar()
        self.tmax_var = tk.DoubleVar()

        tk.Label(frame_seg_1, text="事件前（秒，负值）:", width=20, anchor='w').pack(pady=5,side=tk.LEFT,fill=tk.X)
        tk.Entry(frame_seg_1, textvariable=self.tmin_var, width=20).pack(pady=5,side=tk.RIGHT)

        tk.Label(frame_seg_2, text="事件后（秒）:", width=20, anchor='w').pack(pady=5,side=tk.LEFT,fill=tk.X)
        tk.Entry(frame_seg_2, textvariable=self.tmax_var, width=20).pack(pady=5,side=tk.RIGHT)

        confirm_btn = tk.Button(frame_seg_3, text="确认", width=20, command=self.perform_manual_segmentation)
        confirm_btn.pack()

    def perform_manual_segmentation(self):
        event_id = self.__event_dict[self.event_var.get()]
        tmin = self.tmin_var.get()
        tmax = self.tmax_var.get()
        
        events = np.array(self.__events)
        event_mask = events[:, 2] == event_id
        event_times = np.divide(events[event_mask, 0],self.__raw_data.info['sfreq']).tolist() # 只保留时间戳

        # 检查tmin和tmax有效性
        if tmin < -event_times[0] or tmax > (self.__raw_data.n_times/self.__raw_data.info['sfreq'] - event_times[-1]) or tmax<=tmin:
            messagebox.showerror("错误", "时间范围不合法！请选择合适的时间范围")
            return

        # 调用分割函数
        epochs = mne.Epochs(self.__raw_data, self.__events, event_id=event_id, tmin=tmin, tmax=tmax, preload=True,baseline=(None, None))
        self.raw_seg = epochs
        messagebox.showinfo("信息", "分割完成！")
        self.__master.quit()
        self.__master.destroy()
        
#######################################################################################自动分割###########################################################################################

    def create_auto_window(self):
        auto_window = tk.Toplevel(self.__master)
        auto_window.title("自动分割")
        auto_window.geometry("450x150")
        auto_window.resizable(False, False)

        frame_auto_0 = tk.Frame(auto_window)
        frame_auto_0.pack(side=tk.TOP, pady=10)
        frame_auto_1 = tk.Frame(auto_window)
        frame_auto_1.pack(side=tk.TOP, pady=10)
        frame_auto_2 = tk.Frame(auto_window)
        frame_auto_2.pack(side=tk.TOP, pady=10)

        # 下拉选择框
        tk.Label(frame_auto_0, text="选择初始事件:",anchor='w',width=20).pack(side=tk.LEFT,fill=tk.X)
        self.start_event_var = tk.StringVar()
        self.start_event_dropdown = ttk.Combobox(frame_auto_0, textvariable=self.start_event_var)
        self.start_event_dropdown['values'] = list(self.__event_dict.keys())
        self.start_event_dropdown.pack(side=tk.RIGHT,fill=tk.X)

        tk.Label(frame_auto_1, text="选择结束事件:",anchor='w',width=20).pack(side=tk.LEFT,fill=tk.X)
        self.end_event_var = tk.StringVar()
        self.end_event_dropdown = ttk.Combobox(frame_auto_1, textvariable=self.end_event_var)
        self.end_event_dropdown['values'] = list(self.__event_dict.keys())
        self.end_event_dropdown.pack(side=tk.RIGHT,fill=tk.X)

        confirm_btn = tk.Button(frame_auto_2, text="确认", command=self.perform_auto_segmentation,width=20)
        confirm_btn.pack()
        
    # 根据标记事件来进行分段，包含特殊情况，如hs,hs,to的情况，只会截取第二个hs与to间的片段
    def find_pairs(self, start, end):
        result = []
        end_index = 0
        num_starts = len(start)
        num_ends = len(end)

        # 遍历每一个start
        for i in range(num_starts):
            s = start[i]

            # 寻找第一个大于s的end
            while end_index < num_ends and end[end_index] <= s:
                end_index += 1
            
            # 如果找到了合适的end，确保没有其他start在当前end之前
            if end_index < num_ends:
                # 检查是否为相邻段
                if (i == num_starts - 1 or end[end_index] <= start[i + 1]):
                    result.append((s, end[end_index]))
                    end_index += 1  # 移到下一个end，以避免重复

        return result


    #删除离群值（例如病人在行走过程中停下了，再行走时hs到hs这个步态就包括停顿时间）
    def detect_outliers(self, segments):
        # 计算每个元组的长度
        lengths = [b - a for a, b in segments]
        
        # 计算Q1, Q3和IQR
        Q1 = np.percentile(lengths, 25)
        Q3 = np.percentile(lengths, 75)
        IQR = Q3 - Q1
        
        # 计算离群值的上下限
        lower_bound = Q1 - 1.2 * IQR
        upper_bound = Q3 + 0.9 * IQR
        
        # 找出离群值及其对应的段
        outliers = [segments[i] for i in range(len(lengths)) if lengths[i] < lower_bound or lengths[i] > upper_bound]
        
        # 创建一个副本以避免修改原始列表
        filtered_segments = segments.copy()
        
        # 删除离群值
        for outlier in outliers:
            if outlier in filtered_segments:  # 确保元素存在
                filtered_segments.remove(outlier)
        
        return filtered_segments

    #数据分段
    def segment_data(self, raw,events,start_id,end_id):
        fs = raw.info['sfreq']
        events = np.array(events)
        event_start_mask = events[:, 2] == start_id
        event_start_times = np.divide(events[event_start_mask, 0],fs).tolist() # 只保留时间戳
        event_end_mask = events[:, 2] == end_id
        event_end_times = np.divide(events[event_end_mask, 0],fs).tolist() # 只保留时间戳
        
        # 创建时间片段列表
        epochs = self.find_pairs(event_start_times,event_end_times)
        epochs_filtered = self.detect_outliers(epochs)
        # 创建自定义 epochs
        custom_epochs = []
        
        for tmin, tmax in epochs_filtered:
            # 使用 raw.extract_data() 获取具体的片段数据
            epoch_data = raw.copy().crop(tmin, tmax)
            custom_epochs.append(epoch_data)
        
        return custom_epochs
    
    def perform_auto_segmentation(self):
        start_event_id = self.__event_dict[self.start_event_var.get()]
        end_event_id = self.__event_dict[self.end_event_var.get()]

        # 调用自动分割函数
        segments = self.segment_data(self.__raw_data,self.__events, start_event_id, end_event_id)
        self.raw_seg = segments
        messagebox.showinfo("信息", "自动分割完成！")
        self.__master.quit()
        self.__master.destroy()

def EEGSeg(root,raw,events,event_dict):
    root = tk.Toplevel(root)
    EEG_seg = EEGSegmentation(root,copy.deepcopy(raw),events,event_dict)
    root.mainloop()
    return EEG_seg.raw_seg
