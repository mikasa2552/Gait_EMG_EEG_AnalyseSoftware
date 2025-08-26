import matplotlib
matplotlib.use('TkAgg')  # 设置 Matplotlib 使用 TkAgg 后端
import tkinter as tk
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from scipy import signal
import mne

def apply_filter(raw, low_freq, high_freq):
    #f=raw.info['sfreq']
    #b, a = signal.butter(4, [low_freq*2/f, high_freq*2/f], btype='bandpass', fs=2*f)
    raw_filtered=raw.filter(float(low_freq),float(high_freq),fir_design='firwin')
    return raw_filtered

def update_filter_plot(ax, low_freq, high_freq, raw):
    ax.clear()
    f=raw.info['sfreq']
    b, a = signal.butter(4, [float(low_freq), float(high_freq)], btype='bandpass', fs=2*f)
    w, h = signal.freqz(b, a)
    ax.plot(w * f / (2 * np.pi), np.abs(h),  linestyle='-', color='b')
    ax.set_title('Filter Frequency Response')
    ax.set_xlabel('Frequency (Hz)')
    ax.set_ylabel('Magnitude')
    ax.set_xlim(0, f/2)
    ax.set_ylim(0, 1.2)


def DenoiseEEG(root,raw):
    window = tk.Toplevel(root)
    window.title("Filter Configuration")

    raw_filtered=raw
    
    low_freq = tk.DoubleVar(value=0.5)
    high_freq = tk.DoubleVar(value=50.0)


    def freq_confirm():
        """更新频率确认图"""
        update_filter_plot(ax, low_freq.get(), high_freq.get(), raw)
        canvas.draw()
        # 关闭所有未显示的图形窗口
        plt.close('all')


    def filter_signal():
        nonlocal raw_filtered
        raw_filtered=apply_filter(raw, low_freq.get(), high_freq.get())
        #关闭window
        window.quit()
        window.destroy()

    label_low_freq = tk.Label(window, text='Low Frequency:')
    label_low_freq.grid(row=0, column=0)
    entry_low_freq = tk.Entry(window, textvariable=low_freq)
    entry_low_freq.grid(row=0, column=1)

    label_high_freq = tk.Label(window, text='High Frequency:')
    label_high_freq.grid(row=0, column=2)
    entry_high_freq = tk.Entry(window, textvariable=high_freq)
    entry_high_freq.grid(row=0, column=3)

    fig, ax = plt.subplots()
    canvas = FigureCanvasTkAgg(fig, master=window)
    canvas.get_tk_widget().grid(row=1, column=0,columnspan=4)
    
    button_high_freq = tk.Button(window, text='Confirm', command=freq_confirm)
    button_high_freq.grid(row=2, column=0,columnspan=2)
    # 初始绘图
    update_filter_plot(ax, low_freq.get(), high_freq.get(), raw)

    button_apply = tk.Button(window, text='Apply Filter', command=filter_signal)
    button_apply.grid(row=2, column=2,columnspan=2)
    
    window.grid_rowconfigure(1, weight=1)
    for i in range(4):
        window.grid_columnconfigure(i, weight=1)

    window.mainloop()
    
    return raw_filtered



