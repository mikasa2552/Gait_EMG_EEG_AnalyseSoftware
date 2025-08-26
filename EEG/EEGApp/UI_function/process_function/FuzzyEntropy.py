import EntropyHub as EH
import numpy as np
import mne
import pandas as pd
from alive_progress import alive_bar

def FuzzyEntropy(s:np.ndarray, r=0.15, m=2, n=2):
	th = r * np.std(s)
	return EH.FuzzEn(s, 2, r=(th, n))[0][-1]

def Cal_FuzzEn(raw):
    '''
    计算RAW或单个epoch的最大李亚普洛夫指数
    '''
    raw_data = raw.get_data()
    if raw_data.ndim == 3:
    # 如果是三维数组(即输入是epoch)，执行 np.squeeze
        raw_data= np.squeeze(raw_data)
    FE=[]
    for row in raw_data:
        fe = FuzzyEntropy(row)# 计算模糊熵
        FE.append(fe)
        
    return FE


def EEG_FuzzEn(EEG):
    if type(EEG) == mne.io.edf.edf.RawEDF:
        with alive_bar(
            title="Processing one raw", 
            # 注意：这里 bar 被换成了unknow，内置样式名称与 spinner 的相同
            unknown='waves', spinner='wait'
            ) as bar:
            FE_list = Cal_FuzzEn(EEG)
            FE_mean = np.array(FE_list)
            ch_names = EEG.ch_names
            bar()
    else:        
        FE_list =[]
        with alive_bar(len(EEG),title="Processing all raws") as outbar:
            for i in range(len(EEG)):
                raw = EEG[i]
                FE = Cal_FuzzEn(raw)
                FE_list.append(FE)
                outbar()
        FE_array = np.array(FE_list)
        FE_mean = np.mean(FE_array,axis=0)
        ch_names = raw.ch_names
    data_dict = {
    'Channel': ch_names,  # 横轴的列名
    'FuzzyEntropy': FE_mean # 纵轴的 FE 数据
    }
    # 创建 DataFrame
    df = pd.DataFrame(data_dict)
    return df