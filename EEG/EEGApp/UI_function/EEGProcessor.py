import numpy as np
import matplotlib.pyplot as plt
import copy
import mne
from collections import OrderedDict
from .process_function.OpenEEGfile import OpenEEGfile
from .process_function.epoch_function.OpenEvent import OpenEvent
from .process_function.epoch_function.EventMarker import EventMarker
from .process_function.BadChInter import BadChInter
from .process_function.DenoiseEEG import DenoiseEEG
from .process_function.EEGSeg import EEGSeg
from .process_function.ChannelSelector import Ch_select
from .process_function.ICA_EEG import ICA_EEG
from .process_function.Epoch import Epoch

class EEGProcessor:
    '''EEG的预处理计算'''
    def __init__(self):
        self.states = OrderedDict()  # 用于保存每一步的状态
        self.raw = None
        self.epoch = None
        #选取通道
        self.raw_selected = None
        #坏导插值
        self.raw_intered = None
        #降噪
        self.raw_filtered = None
        #ICA
        self.raw_ica = None
        #选取通道
        self.raw_ICA_selected = None
        #脑电信号分段
        self.raw_epoch = None
        #基线数据
        self.raw_base_epoch = None
        #基线校准
        self.raw_epoch = None
        
    def update_and_move_to_end(self,ordered_dict, key_value_pair):
        """
        更新有序字典中的指定键的值，并将其移动到字典的末尾。
        
        参数：
        ordered_dict (OrderedDict): 原有的有序字典
        key_value_pair (tuple): 包含新键和值的元组，例如 ('b', 20)
        """
        key_to_update, new_value = key_value_pair
    
        # 删除原有键值对（如果存在）
        if key_to_update in ordered_dict:
            del ordered_dict[key_to_update]
        
        # 重新添加键值对到末尾
        ordered_dict[key_to_update] = new_value
        return ordered_dict
        
    def add_state(self, state, result):
        """保存当前状态的深拷贝"""
        self.states=self.update_and_move_to_end(self.states,(state,copy.deepcopy(result)))

    def load_data(self):
        """加载EEG数据并保存状态"""
        self.raw = OpenEEGfile()
        self.add_state("已导入原始数据！",self.raw)
        
    def load_evt(self,root,isDevide):
        """加载event数据并保存状态"""
        self.epoch = Epoch(root,isDevide)
        self.add_state("已导入事件！",self.epoch)

    def select_channels(self,root):
        """选择通道并保存状态"""
        self.raw_selected = Ch_select(root,copy.deepcopy(self.states["已导入原始数据！"]))
        self.add_state("已选择预处理通道！",self.raw_selected)

    def interpolate_bad_channels(self,root):
        """坏导插值并保存状态""" 
        self.raw_intered = BadChInter(root,copy.deepcopy(self.states["已选择预处理通道！"]))
        print(self.raw_intered.info['bads'])
        self.add_state("坏导已插值！",self.raw_intered)

    def denoise(self,root):
        """降噪并保存状态"""
        self.raw_filtered = DenoiseEEG(root,copy.deepcopy(self.states["坏导已插值！"]))
        self.add_state("已降噪！",self.raw_filtered)

    def apply_ica(self,root):
        """应用ICA并保存状态"""
        self.raw_ica = ICA_EEG(root,copy.deepcopy(self.states["已降噪！"]))
        self.add_state("ICA去除伪迹完成！",self.raw_ica)

    def select_ica_channels(self,root):
        """选择ICA通道并保存状态"""
        self.raw_ICA_selected = Ch_select(root,copy.deepcopy(self.states["ICA去除伪迹完成！"]))
        self.add_state("已选择后处理通道！",self.raw_ICA_selected)

    def segment_eeg(self,root):
        """分段EEG数据并保存状态"""
        self.raw_epoch = EEGSeg(root,copy.deepcopy(self.states["已选择后处理通道！"]), self.epoch.Event, self.epoch.Event_dic)
        self.add_state("分割完成！",self.raw_epoch)

    
    def base_process(self,root):
        plt.close('all')
        raw_base = OpenEEGfile()
        #获取其事件数据
        raw_base_event,base_time_list = OpenEvent()
        #处理事件数据形成标准化
        #base_dic = {key: int(key) for key in raw_base_event}
        base_dic =  EventMarker(root,raw_base_event)
        base_time_list = [float(num) for num in base_time_list]
        base_event = self.EventCreat(raw_base_event,base_time_list,base_dic)
        raw_base_selected = Ch_select(root,raw_base)
        raw_base_selected.plot(n_channels=len(raw_base_selected.ch_names),scalings='auto', title="已选择预处理通道！",show=True,remove_dc=True)
        plt.show() 
        plt.close('all')# 阻塞，直到图形窗口关闭
        raw_base_intered=BadChInter(root,raw_base_selected )
        raw_base_filtered = DenoiseEEG(root,raw_base_intered)
        raw_base_filtered.plot(n_channels=len(raw_base_filtered.ch_names),scalings='auto', title="已降噪！", show=True,remove_dc=True)
        plt.show() 
        plt.close('all')# 阻塞，直到图形窗口关闭
        raw_base_ica = ICA_EEG(root,raw_base_filtered)
        raw_base_ica.plot(n_channels=len(raw_base_ica.ch_names),scalings='auto', title="ICA去除伪迹完成！", show=True,remove_dc=True)
        plt.show()
        plt.close('all')# 阻塞，直到图形窗口关闭
        raw_base_ICA_selected = Ch_select(root,raw_base_ica)
        self.raw_base_epoch = EEGSeg(root,raw_base_ICA_selected, base_event,base_dic)
        #self.raw_base_epoch.plot(n_channels=len(self.raw_base_epoch.ch_names),scalings='auto', title="分割完成！", show=False,remove_dc=True)
        if type(self.raw_base_epoch)!= list:
            self.raw_base_epoch.plot(n_channels=len(self.raw_base_epoch.ch_names),scalings='auto', title="分割完成！", show=False,remove_dc=True)
        else:
            mne.io.concatenate_raws(copy.deepcopy(self.raw_base_epoch)).plot(title="分割完成！",scalings='auto',show=False,remove_dc=True)
        plt.show()
        plt.close('all')# 阻塞，直到图形窗口关闭


    def base_aligned(self):
            self.raw_epoch = self.states["分割完成！"]
            base_line = np.mean(self.raw_base_epoch.average().get_data(),axis=1)
            base_line = base_line.reshape((len(base_line), 1))
            for raw in self.raw_epoch:
                data = raw.get_data()  # 获取原始数据
                tmp = data - base_line  # 对数据执行操作
                raw._data[:] = tmp  # 更新原始数据
            self.add_state("已完成基线校准！",self.raw_epoch)
        

    def EventCreat(self,event_names,event_times,event_dic):
        event_ids = np.array([event_dic[name] for name in event_names])
        events = np.array([[int(time * 1000), 0, event_id] for time, event_id in zip(event_times, event_ids)])
        return events
