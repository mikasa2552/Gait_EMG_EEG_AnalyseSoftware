import numpy as np
import mne
import pandas as pd
from alive_progress import alive_bar
import tkinter as tk
from tkinter import ttk, messagebox
import queue
import threading
from scipy.stats import linregress
from .Lyapunov_Function.lyapunov import mle_embed
from .Lyapunov_Function.lyapunov_gpu import mle_embed_gpu
import time
import traceback

class MLEProcessor:
    def __init__(self, root, raw, use_gpu=False, dim=None, tau=None, maxt=None, window=None):
        self.root = root
        self.raw = raw
        self.use_gpu = use_gpu
        self.dim = dim
        self.tau = tau
        self.maxt = maxt
        self.window = window
        self.result_queue = queue.Queue()
        self.mle_df = None
        self.stop_event = threading.Event()

    def cal_mle(self, raw):
        raw_data = raw.get_data()
        if raw_data.ndim == 3:
            raw_data = np.squeeze(raw_data)  # 从 [N,1,M] 转为 [N,M]
        
        mle_results = []
        for i, row in enumerate(raw_data):
            if self.stop_event.is_set():
                break

            try:
            # 调用MLE计算（GPU/CPU）
                print(f"💻 正在计算脑电通道（{i+1}/{len(raw_data)}）...")
               
                if self.use_gpu:
                        d_mle = mle_embed_gpu(
                            row, 
                            dim=self.dim, 
                            tau=self.tau, 
                            maxt=self.maxt, 
                            window=self.window
                        )

                else:
                    d_mle = mle_embed(
                        row,
                        dim=self.dim,
                        tau=self.tau,
                        maxt=self.maxt,
                        window=self.window
                    )

                # 结果标准化处理
                d_mle = np.asarray(d_mle, dtype=np.float64).flatten()  # 强制转为1维数组
                # 有效性检查
                if len(d_mle) == 0:
                    raise ValueError("返回结果为空数组")
                    
                valid_mask = ~np.isnan(d_mle) & ~np.isinf(d_mle)
                d_valid = d_mle[valid_mask]

                # 线性回归计算斜率
                if len(d_valid) >= 2:  # 至少需要2个点做回归
                    slope, _, _, _, _ = linregress(
                        x=np.arange(len(d_valid)),
                        y=d_valid
                    )
                else:
                    slope = np.nan
                    
                mle_results.append(slope)
                
            except Exception as e:
                traceback.print_exc()
                print(f"Data shape: {row.shape} | MLE result: {d_mle if 'd_mle' in locals() else 'N/A'}")
                mle_results.append(np.nan)
                continue
                
        return mle_results

    def eeg_mle(self, eeg):
        if isinstance(eeg, mne.io.edf.edf.RawEDF):
            with alive_bar(title="Processing one raw", unknown='waves', spinner='wait') as bar:
                mle_list = self.cal_mle(eeg)
                mle_mean = np.array(mle_list)
                ch_names = eeg.ch_names
                bar()
        else:
            mle_list = []
            with alive_bar(len(eeg), title="Processing all raws") as outbar:
                for i in range(len(eeg)):
                    if self.stop_event.is_set():
                        break
                    raw = eeg[i]
                    mle = self.cal_mle(raw)
                    mle_list.append(mle)
                    outbar()
            mle_array = np.array(mle_list)
            mle_mean = np.mean(mle_array, axis=0)
            ch_names = raw.ch_names
        data_dict = {'Channel': ch_names, 'MLE': mle_mean}
        df = pd.DataFrame(data_dict)
        return df

    def mle_process(self):
        df = self.eeg_mle(self.raw)
        return df

    def run_mle(self):
        result = self.mle_process()
        self.result_queue.put(result)

    def show_monitor_window(self):
        monitor_window = tk.Toplevel(self.root)
        monitor_window.title("MLE计算进度")
        self.progress = ttk.Progressbar(monitor_window, orient="horizontal", length=300, mode="indeterminate")
        self.progress.pack(pady=20)
        self.progress.start()
        self.cancel_button = tk.Button(monitor_window, text="取消", command=self.cancel)
        self.cancel_button.pack(pady=10)
        return monitor_window

    def cancel(self):
        self.stop_event.set()
        self.result_queue.put(None)

    def check_queue(self, monitor_window):
        try:
            result = self.result_queue.get_nowait()
            monitor_window.destroy()
            self.mle_df = result
        except queue.Empty:
            self.root.after(100, lambda: self.check_queue(monitor_window))

    def start_mle(self):
        if self.use_gpu:
            # 如果使用 GPU，直接运行 MLE 计算并返回结果
            self.mle_df = self.mle_process()
        else:
            # 如果不使用 GPU，显示监视窗口并使用多线程
            monitor_window = self.show_monitor_window()
            threading.Thread(target=self.run_mle, daemon=True).start()
            self.root.after(100, lambda: self.check_queue(monitor_window))

    def get_result(self):
        while self.mle_df is None:
            self.root.update_idletasks()  # 仅处理挂起的 GUI 事件，不阻塞
            self.root.update()  # 处理所有事件
            time.sleep(0.1)  # 避免 CPU 占用过高
        return self.mle_df


def MLE(root, raw, callback):
    # 弹出窗口选择是否使用 GPU 加速
    def ask_gpu():
        gpu_window = tk.Toplevel(root)
        gpu_window.title("选择 GPU 加速")
        tk.Label(gpu_window, text="是否使用 GPU 加速？\n（仅可在独立显卡中使用，且配置了 CUDA 环境）").grid(row=0, column=0, columnspan=2, pady=5, padx=10)
        def select_yes():
            gpu_window.destroy()
            ask_parameters(use_gpu=True)
        def select_no():
            gpu_window.destroy()
            ask_parameters(use_gpu=False)
        tk.Button(gpu_window, text="是", command=select_yes).grid(row=1, column=0, columnspan=1, pady=5, padx=10)
        tk.Button(gpu_window, text="否", command=select_no).grid(row=1, column=1, columnspan=1, pady=5, padx=10)

    # 弹出窗口输入参数
    def ask_parameters(use_gpu):
        param_window = tk.Toplevel(root)
        param_window.title("输入参数")
        # 推荐的默认值
        default_dim = [3]  # 嵌入维度
        default_tau = 10  # 时间延迟
        default_maxt = 100  # 最大时间
        default_window = 50  # 窗口大小
        tk.Label(param_window, text="请输入以下参数：").pack(pady=10)
        # 输入 dim
        tk.Label(param_window, text="嵌入维度 (dim):").pack()
        dim_entry = tk.Entry(param_window)
        dim_entry.insert(0, str(default_dim))
        dim_entry.pack()
        # 输入 tau
        tk.Label(param_window, text="时间延迟 (tau):").pack()
        tau_entry = tk.Entry(param_window)
        tau_entry.insert(0, str(default_tau))
        tau_entry.pack()
        # 输入 maxt
        tk.Label(param_window, text="最大时间 (maxt):").pack()
        maxt_entry = tk.Entry(param_window)
        maxt_entry.insert(0, str(default_maxt))
        maxt_entry.pack()
        # 输入 window
        tk.Label(param_window, text="窗口大小 (window):").pack()
        window_entry = tk.Entry(param_window)
        window_entry.insert(0, str(default_window))
        window_entry.pack()
        # 提示信息
        tk.Label(param_window, text="推荐值：\n"
                                   "dim: [3] (嵌入维度)\n"
                                   "tau: 10-50 (时间延迟)\n"
                                   "maxt:信号长度（时间*采样频率）的5% (最大时间)\n"
                                   "window: maxt/2 (窗口大小)").pack(pady=10)
        def confirm():
            try:
                dim = eval(dim_entry.get())  # 将字符串转换为列表
                tau = int(tau_entry.get())
                maxt = int(maxt_entry.get())
                window = int(window_entry.get())
                param_window.destroy()
                processor = MLEProcessor(root, raw, use_gpu, dim, tau, maxt, window)
                processor.start_mle()
                result = processor.get_result()  # 获取结果
                callback(result)  # 将结果传递给回调函数
            except Exception as e:
                messagebox.showerror("错误", f"参数输入无效：{e}")
        tk.Button(param_window, text="确认", command=confirm).pack(pady=10)

    ask_gpu()