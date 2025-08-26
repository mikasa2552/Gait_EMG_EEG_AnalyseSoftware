import numpy as np
from .analysis import pdc
from scipy.fftpack import fft, ifft
from alive_progress import alive_bar
import numpy as np

def analyze_pdc(eeg_list, sampling_rate=1000, n_freq=256, alpha=0.05):
    """
    分析脑电数据的 PDC 矩阵，返回每个频段的保留权重矩阵和二值矩阵。

    参数:
        eeg_list (list): 包含 l 个 epoch 的列表，每个 epoch 是一个 n_channels * n_samples 的矩阵。
        sampling_rate (int): 采样率，默认 1000 Hz。
        n_freq (int): PDC 矩阵的频率分辨率，默认 128。
        alpha (float): 显著性水平，默认 0.05。

    返回:
        dict: 每个频段的保留权重矩阵和二值矩阵。
    """
    # 定义频段
    bands = {
        'Delta (0.5-4 Hz)':(0.5, 4),
        'Theta (4-8 Hz)': (4, 8),
        'Alpha (8-13 Hz)': (8, 13),
        'Beta (13-30 Hz)': (13, 30),
        'Gamma (30-50 Hz)': (30, 50)
        }
    
    def pdc_cal(data):
        pdc_matrix = pdc(data, maxp=20, nf=128, detrend=True, normalize=True, ss=True, fixp=True)
        # 将 PDC 矩阵的对角线设为 0
        for i in range(pdc_matrix.shape[0]):
            for j in range(pdc_matrix.shape[1]):
                if i == j:
                    pdc_matrix[i, j, :] = 0
        return pdc_matrix
    
        # 如果 l < 50，进行相位随机化
    if len(eeg_list) < 50:
        # 相位随机化函数
        def phase_randomization(data):
            n_channels, n_samples = data.shape
            surrogate_data = np.zeros_like(data)
            for i in range(n_channels):
                # 进行 FFT
                fft_data = fft(data[i])
                # 随机化相位
                random_phases = np.exp(2j * np.pi * np.random.rand(len(fft_data)))
                fft_data_randomized = fft_data * random_phases
                # 进行逆 FFT
                surrogate_data[i] = np.real(ifft(fft_data_randomized))
            return surrogate_data

        # 计算每个数据需要生成的替代数据数量
        n_surrogates_per_data = (50 - len(eeg_list)) // len(eeg_list) + 1
        surrogates = []  # 存储生成的替代数据

        # 计算总进度条数量
        total_iterations = len(eeg_list) * n_surrogates_per_data

        with alive_bar(total_iterations, title="相位随机化") as bar:
            for data in eeg_list:
                for _ in range(n_surrogates_per_data):
                    surrogate_data = phase_randomization(data)
                    surrogates.append(surrogate_data)
                    bar()
        eeg_list.extend(surrogates)
    

    # 频率轴
    freq_axis = np.linspace(0, sampling_rate / 2, n_freq)
    
    #计算PDC
    pdc_matrices=[]
    with alive_bar(len(eeg_list), title="Processing PDC") as outbar:
        for data in eeg_list:
            pdc_matrices.append(pdc_cal(data))
            outbar()
        
    # 提取频段 PDC 矩阵
    def extract_band_pdc(pdc_matrix, low_freq, high_freq):
        freq_indices = np.where((freq_axis >= low_freq) & (freq_axis <= high_freq))[0]
        return np.mean(np.abs(pdc_matrix[:, :, freq_indices]), axis=2)

    band_pdc_matrices = {band_name: [] for band_name in bands}
    for pdc_matrix in pdc_matrices:
        for band_name, (low_freq, high_freq) in bands.items():
            band_pdc_matrices[band_name].append(extract_band_pdc(pdc_matrix, low_freq, high_freq))


    # 对每个频段的 PDC 矩阵进行平均和显著性检验
    band_results = {}
    for band_name, pdc_list in band_pdc_matrices.items():
        # 计算平均 PDC 矩阵
        average_pdc_matrix = np.mean(pdc_list, axis=0)
        
        # 置换检验
        null_distribution = []
        for _ in range(100):  # 100 次置换
            shuffled_pdc = np.stack([np.random.permutation(pdc) for pdc in pdc_list])
            null_distribution.append(np.mean(shuffled_pdc, axis=0))
        
        # 计算阈值矩阵
        threshold_matrix = np.percentile(null_distribution, 100 * (1 - alpha), axis=0)
        
        # 生成保留权重的 PDC 矩阵
        weighted_pdc_matrix = np.where(average_pdc_matrix >= threshold_matrix, average_pdc_matrix, 0)
        
        # 生成二值矩阵
        binary_matrix = (average_pdc_matrix >= threshold_matrix).astype(int)
        
        # 保存结果
        band_results[band_name] = {
            'weighted_pdc_matrix': weighted_pdc_matrix,
            'binary_matrix': binary_matrix
        }
        

    return band_results