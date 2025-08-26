from .epoch_function.EventMarker import EventMarker
from .epoch_function.GE_times_trans import GE_times_trans
from .epoch_function.OpenEvent import OpenEvent, OpenGEfile
import numpy as np
import tkinter as tk
from tkinter import messagebox

class Epoch():
    def __init__(self, root,isDevide):

        # 如果用户选择“是”，则继续运行计算函数
        if isDevide:
             # 脑电tigger事件的事件名称和对应的time
            self.__Event_Name_list, self.__Event_Time_list = OpenEvent()
            # 步态事件在100hz的情况下的事件名称和对应的frame
            self.__GE_Event_dic, self.__GE_Frame_dic = OpenGEfile()
            # 将步态事件一一对应应用在脑电数据中
            self.__GE_EEG_list, self.__GE_EEG_Times_list = GE_times_trans(root, self.__GE_Event_dic, self.__GE_Frame_dic, self.__Event_Name_list, self.__Event_Time_list)
            # 将步态事件进行标记
            self.Event_dic = EventMarker(root, self.__GE_EEG_list)
            self.Event = self.__EventCreat(self.__GE_EEG_list, self.__GE_EEG_Times_list, self.Event_dic)
        else:
            # 脑电tigger事件的事件名称和对应的time
            self.__Event_Name_list, self.__Event_Time_list = OpenEvent()
            #处理事件数据形成标准化
            #self.Event_dic = {key: key if isinstance(key, int) else int(key) if isinstance(key, str) and key.isdigit() else key for key in self.__Event_Name_list}
            self.Event_dic = EventMarker(root, self.__Event_Name_list)
            time_list = [float(num) for num in self.__Event_Time_list]
            self.Event = self.__EventCreat(self.__Event_Name_list,time_list,self.Event_dic)


    def __EventCreat(self, event_names, event_times, event_dic):
        event_ids = np.array([event_dic[name] for name in event_names])
        events = np.array([[int(time * 1000), 0, event_id] for time, event_id in zip(event_times, event_ids)])
        return events
    