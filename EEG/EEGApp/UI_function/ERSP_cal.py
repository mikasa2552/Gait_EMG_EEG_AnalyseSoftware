from scipy.interpolate import interp1d
import numpy as np
import tkinter as tk
import matplotlib.pyplot as plt
from tkinter.filedialog import asksaveasfilename
from tkinter import messagebox
import pandas as pd

def ERSP_cal(root,raw,base):
    master = tk.Toplevel(root)
    master.title("请设置相关参数！")
    low_freq = tk.DoubleVar(value=0)
    high_freq = tk.DoubleVar(value=0)
    num = tk.IntVar(value=0)

    label_low_freq = tk.Label(master, text='Low Frequency:')
    label_low_freq.grid(row=0, column=0,pady=10,padx=10)
    entry_low_freq = tk.Entry(master, textvariable=low_freq)
    entry_low_freq.grid(row=0, column=1,pady=10,padx=10)

    label_high_freq = tk.Label(master, text='High Frequency:')
    label_high_freq.grid(row=0, column=2,pady=10,padx=10)
    entry_high_freq = tk.Entry(master, textvariable=high_freq)
    entry_high_freq.grid(row=0, column=3,pady=10,padx=10)

    label_num = tk.Label(master, text='Num of frequence')
    label_num.grid(row=0, column=4,pady=10,padx=10)
    entry_num = tk.Entry(master, textvariable=num)
    entry_num.grid(row=0, column=5,pady=10,padx=10)

    def ersp_draw(raw_list,base):
        freqs = np.logspace(*np.log10([low_freq.get(), high_freq.get()]), num=num.get())
        n_cycles = freqs / 2.
        power_base= base.compute_tfr(method='morlet', freqs=freqs, n_cycles=n_cycles,average=True)
        mean_base = np.mean(power_base.get_data(), axis=2) 
        power_raw_aligned_list=[]
        for raw in raw_list:
            power_raw=raw.compute_tfr(method='morlet', freqs=freqs, n_cycles=n_cycles)
            power_raw_array=power_raw.get_data()
            power_raw_aligned=(power_raw_array-mean_base[:,:,np.newaxis])/mean_base[:, :, np.newaxis]
            min_power_raw_aligned = np.min(power_raw_aligned)  # 找到 c 的最小值

            if min_power_raw_aligned < 0:
                shift_value = abs(min_power_raw_aligned) + 1e-10  # 需要添加的常数
                power_raw_aligned += shift_value  # 平移 

            # 对 c 求对数
            log_power_raw_aligned = np.log10(power_raw_aligned)
            power_raw_aligned_list.append(log_power_raw_aligned)


        def resample_array(arr, target_length=1000):
            a, b, n = arr.shape
            # 创建新的数组
            resampled_arr = np.zeros((a, b, target_length))
            
            # 进行重采样
            for i in range(a):
                for j in range(b):
                    # 获取当前的列，并进行插值
                    y = arr[i, j, :]
                    x_old = np.linspace(0, 1, n)  # 原始 x 坐标
                    x_new = np.linspace(0, 1, target_length)  # 新的 x 坐标
                    
                    # 使用一维插值
                    interp_func = interp1d(x_old, y, kind='linear', fill_value='extrapolate')
                    resampled_arr[i, j, :] = interp_func(x_new)

            return resampled_arr


        # 对每个数组进行重采样
        resampled_arrays = [resample_array(arr) for arr in power_raw_aligned_list]
        array_stack = np.array(resampled_arrays)

        # 计算平均值
        average_array = np.mean(array_stack, axis=0)
        # 绘制平均 TFR 的示例
        for channel in range(average_array.shape[0]):
            plt.figure()
            plt.imshow(average_array[channel, :, :], aspect='auto', extent=[0, 1, 1, 30], origin='lower', interpolation='bilinear')
            
            plt.colorbar(label='Power')
            plt.title(f'Average TFR for Channel {channel + 1}')
            plt.xlabel('Time (s)')
            plt.ylabel('Frequency (Hz)')
            plt.yticks(freqs)  # 设置 y 轴刻度为实际的频率值

            plt.xlim(0, 1)  # 设置 x 轴范围
            plt.show()
            # 创建一个 DataFrame
            df = pd.DataFrame(average_array[channel, :, :])

            # 设置表头，y轴为实际的频率值
            # 在 DataFrame 中添加频率值作为列名
            df.columns = [f'Time {i}' for i in range(1000)]  # 设置时间列名
            df.index = freqs  # 设置频率值为行索引
            # 创建 Tkinter 窗口

            # 弹出文件保存对话框
            excel_filename = asksaveasfilename(defaultextension=".xlsx",
                                                filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
                                                title="Save Excel File")
                                                
            if excel_filename:  # 检查用户是否选择了文件名
                # 将 DataFrame 导出为 Excel 文件
                df.to_excel(excel_filename, sheet_name='Average TFR')

            else:
                messagebox.showwarning("Warning!","取消保存!")
        

    def confirm():
        ersp_draw(raw,base)
        master.quit()
        master.destroy()

    confirm_button = tk.Button(master, text='Confirm',command=confirm,width=40)
    confirm_button.grid(row=1, column=2,columnspan=2,pady=20,padx=10)

    master.mainloop()
