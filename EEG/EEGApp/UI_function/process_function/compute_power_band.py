import numpy as np
import pandas as pd
import mne
import logging
# 设置日志级别为WARNING，抑制INFO级别的信息
logging.getLogger('mne').setLevel(logging.WARNING)

def compute_power_band(raw):
    '''计算不同频段的脑电信号'''
    if type(raw) == list:
        n = len(raw)
        spectrum_list = []
        for i in range(n):
            psd = raw[i].compute_psd(method='welch', fmin=0.5, fmax=40, n_fft=512,n_overlap=256)
            spectrum_list.append(psd.get_data())
        spectrum_array = np.stack(spectrum_list, axis=0)
        psd._data[:] = np.mean(spectrum_array,axis=0)
    elif type(raw) == mne.epochs.Epochs:
        psd = raw.compute_psd(method='welch', fmin=0.5, fmax=40, n_fft=512,n_overlap=256)
        psd = psd.average()
    else:        
        psd = raw.compute_psd(method='welch', fmin=0.5, fmax=40, n_fft=512,n_overlap=256)
        
    psd_data = psd.get_data()  
    frequencies = psd.freqs  # 频率数组
    Δf = frequencies[1] - frequencies[0]  # 计算频率间隔
    # 定义频段
    iter_freqs = [
        {'name': 'Delta', 'fmin': 0.5, 'fmax': 4},
        {'name': 'Theta', 'fmin': 4, 'fmax': 8},
        {'name': 'Alpha', 'fmin': 8, 'fmax': 13},
        {'name': 'Low Beta',  'fmin': 13, 'fmax': 20},
        {'name': 'High Beta',  'fmin': 20, 'fmax': 30},
    ]

    # 初始化一个字典来存储每个通道在各频段的能量
    energy_per_band = {band['name']: np.zeros(psd_data.shape[0]) for band in iter_freqs}

    # 计算每个频段的能量
    for band in iter_freqs:
        fmin = band['fmin']
        fmax = band['fmax']
        freq_indices = np.where((frequencies >= fmin) & (frequencies < fmax))[0]
        
        for channel_index in range(psd_data.shape[0]):
            # 计算能量：积分并转换单位到 μV²
            energy = np.sum(psd_data[channel_index, freq_indices] * Δf) * 1e12
            energy_per_band[band['name']][channel_index] = energy
            
    # 创建 DataFrame
    channel_names = psd.ch_names  # 通道名称列表
    energy_df = pd.DataFrame(energy_per_band, index=channel_names)
    return energy_df