import mne
import tkinter as tk
from tkinter import messagebox,ttk
from tkinter.filedialog import asksaveasfilename
import copy
from .UI_function.EEGProcessor import EEGProcessor
from .UI_function.Button_Customize import Button_Customize
from .UI_function.ERSP_cal import ERSP_cal
from .UI_function.process_function.compute_power_band import compute_power_band
from .UI_function.process_function.EEG_MLE import MLE
from .UI_function.process_function.FuzzyEntropy import EEG_FuzzEn
from .UI_function.process_function.eeg_pdc import eeg_pdc

class EEGApp(EEGProcessor):
    def __init__(self, master):
        super().__init__()  # 先调用父类的初始化
        self.__master = master
        self.__master.title("EEG Processing App")
        # 当窗口关闭时调用的函数
        self.__master.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.notebook = ttk.Notebook(self.__master )
        
        # 将 Notebook 添加到主窗口中
        self.notebook.pack(expand=True, fill='both')
        
        # 创建第一个选项卡
        self.tab1 = ttk.Frame(self.notebook)
        self.notebook.add(self.tab1, text='预处理')
        # 创建第二个选项卡
        self.tab2 = ttk.Frame(self.notebook)
        self.notebook.add(self.tab2, text='后处理')

        # 加载数据按钮
        self.load_button = Button_Customize(self.tab1, text="Load Data",command=lambda:(self.load_data(), self.update_label()),
                                            width=20,font=('微软雅黑', 10, 'bold'),bg="lightblue",activebackground='#B6D0E2')
        self.load_button.grid(row=0, column=0,columnspan=1,pady=10,padx=10)
        
        # 加载数据按钮
        self.load_evt_button = Button_Customize(self.tab1, text="Load Event", command=lambda:(self.Devide_Epoch(),self.load_evt(self.tab1,self.__subdivide_events), self.update_label()),
                                                width=20,font=('微软雅黑', 10, 'bold'),bg="lightblue",activebackground='#B6D0E2')
        self.load_evt_button.grid(row=1, column=0,columnspan=1,pady=10,padx=10)

        # 下一步按钮
        next_button = Button_Customize(self.tab1, text="Next Step", command=lambda:(self.next_step(), self.update_label()),
                                       width=20,font=('微软雅黑', 10, 'bold'),bg="lightblue",activebackground='#B6D0E2')
        next_button.grid(row=2, column=0,columnspan=1,pady=10,padx=10)
        
        # 基线导入按钮
        baseline_button = Button_Customize(self.tab1, text="LoadBaseLine", command=self.base_calibrated,
                                       width=15,font=('微软雅黑', 10, 'bold'),bg="lightblue",activebackground='#B6D0E2')
        baseline_button.grid(row=2, column=1,columnspan=1,pady=10,padx=10)

        # 基线校准按钮
        baseline_button = Button_Customize(self.tab1, text="BaseAligned", command=lambda:(self.base_alig(),self.update_label()),
                                       width=15,font=('微软雅黑', 10, 'bold'),bg="lightblue",activebackground='#B6D0E2')
        baseline_button.grid(row=2, column=2,columnspan=1,pady=10,padx=10)
        
        # 绘图按钮
        draw_button = Button_Customize(self.tab1, text="Draw", command=self.draw_raw,
                                       width=60,font=('微软雅黑', 10, 'bold'),bg="lightblue",activebackground='#B6D0E2')
        draw_button.grid(row=3, column=0,columnspan=3,pady=10,padx=10)

        # 下拉选择框
        self.label = tk.Label(self.tab1, width=8,text="选择状态:",font=('微软雅黑', 15, 'bold'),anchor='w')
        self.label.grid(row=1, column=1,columnspan=1,pady=10,sticky='e')

        self.states_var = tk.StringVar()
        self.states_dropdown = ttk.Combobox(self.tab1, textvariable=self.states_var, width=20)
        self.states_dropdown['values'] = list(self.states.keys())
        self.states_dropdown.grid(row=1, column=2,columnspan=1,pady=10,sticky='w')

        # 显示当前状态
        self.current_state_text = tk.Label(self.tab1,width=8, text="当前状态：",font=('微软雅黑', 15, 'bold'),anchor='w')
        self.current_state_text.grid(row=0, column=1,columnspan=1,pady=10,sticky='e')
        self.current_state_label = tk.Label(self.tab1, text="",width=14,foreground='red',relief=tk.SUNKEN,font=('微软雅黑', 13, 'bold'),anchor='w')
        self.current_state_label.grid(row=0, column=2,columnspan=1,pady=10,sticky='w')
        
    #####################################################后处理#########################################
        # ERSP按钮
        ERSP_button = Button_Customize(self.tab2, text="ERSP", command=self.ERSP_Cal,
                                       width=20,font=('微软雅黑', 10, 'bold'),bg="lightblue",activebackground='#B6D0E2')
        ERSP_button.grid(row=0, column=0,columnspan=1,pady=10,padx=10)
        # 计算不同频段功率按钮
        PSD_button = Button_Customize(self.tab2, text="PSD", command=self.PSD_Cal,
                                       width=20,font=('微软雅黑', 10, 'bold'),bg="lightblue",activebackground='#B6D0E2')
        PSD_button.grid(row=0, column=1,columnspan=1,pady=10,padx=10)
        # 计算最大李雅普洛夫指数按钮
        MLE_button = Button_Customize(self.tab2, text="MLE", command=self.MLE_Cal,
                                       width=20,font=('微软雅黑', 10, 'bold'),bg="lightblue",activebackground='#B6D0E2')
        MLE_button.grid(row=1, column=0,columnspan=1,pady=10,padx=10)
        
        # 计算模糊熵按钮
        FuzzEn_button = Button_Customize(self.tab2, text="FuzzyEntropy", command=self.FuzzEn_Cal,
                                       width=20,font=('微软雅黑', 10, 'bold'),bg="lightblue",activebackground='#B6D0E2')
        FuzzEn_button.grid(row=1, column=1,columnspan=1,pady=10,padx=10)

        # 计算PDC
        PDC_button = Button_Customize(self.tab2, text="PDC", command=self.PDC_Cal,
                                       width=20,font=('微软雅黑', 10, 'bold'),bg="lightblue",activebackground='#B6D0E2')
        PDC_button.grid(row=2, column=0,columnspan=1,pady=10,padx=10)

        




    def update_label(self):
        
        if not self.states:
            messagebox.showerror("错误", "请提前导入脑电数据和事件信息")
            return
        else:
        # 更新标签的文本
            current_state = next(reversed(self.states))
            self.current_state_label.config(text=current_state)
            self.states_dropdown['values'] = list(self.states.keys())
        
        if self.states:
        # 设置最后一个选项为默认选项
            self.states_dropdown.current(len(self.states) - 1)
    
    def remove_elements_after_key(self,ordered_dict, key_to_remove_after):
        """
        从有序字典中删除指定键之后的所有元素。

        :param ordered_dict: OrderedDict 要处理的有序字典
        :param key_to_remove_after: str 指定的键，删除该键之后的所有元素
        :return: OrderedDict 修改后的有序字典
        """
        # 检查键是否存在
        if key_to_remove_after in ordered_dict:
            # 找到该键的索引
            keys = list(ordered_dict.keys())
            index = keys.index(key_to_remove_after)

            # 删除该索引之后的所有元素
            for key in keys[index + 1:]:
                del ordered_dict[key]

        return ordered_dict
    
    def Devide_Epoch(self):
        self.subdivide_window = tk.Toplevel(self.__master)
        self.subdivide_window.title("细分事件")

        # 添加提示文本
        label = tk.Label(self.subdivide_window, text="是否细分事件？")
        label.grid(row=0, column=0,columnspan=2,pady=10,padx=10)

        # 添加“是”按钮
        yes_button = tk.Button(self.subdivide_window, text="是", command=self.__on_yes)
        yes_button.grid(row=1, column=0,columnspan=1,pady=10,padx=10)

        # 添加“否”按钮
        no_button = tk.Button(self.subdivide_window, text="否", command=self.__on_no)
        no_button.grid(row=1, column=1,columnspan=1,pady=10,padx=10)
                # 等待用户选择
        self.subdivide_window.grab_set()  # 使子窗口成为模态窗口
        self.__master.wait_window(self.subdivide_window)  # 等待子窗口关闭
    
    def __on_yes(self):
        self.__subdivide_events = True  # 用户选择“是”
        self.subdivide_window.destroy()  # 关闭子窗口

    def __on_no(self):
        self.__subdivide_events = False  # 用户选择“否”
        self.subdivide_window.destroy()  # 关闭子窗口
    
    def next_step(self):
        if not self.states:
            return
        else:
            #current_state = next(reversed(self.states))
            current_state = self.states_dropdown.get()
        if (current_state == "已导入原始数据！" and "已导入事件！" in self.states) or (current_state == "已导入事件！" and "已导入原始数据！" in self.states):
            self.select_channels(self.tab1)
        elif current_state == "已选择预处理通道！":
            self.interpolate_bad_channels(self.tab1)
        elif current_state == "坏导已插值！":
            self.denoise(self.tab1)
        elif current_state == "已降噪！":
            self.apply_ica(self.__master)
        elif current_state == "ICA去除伪迹完成！":
            self.select_ica_channels(self.tab1)
        elif current_state == "已选择后处理通道！":
            self.segment_eeg(self.tab1)
        elif current_state == "分割完成！":
            messagebox.showinfo("提醒", "已完成EEG所有预处理")
        else:
            messagebox.showerror("错误", "请提前导入脑电数据和事件信息")
            return 
        
    def base_calibrated(self):
        self.base_process(self.tab1)
        messagebox.showinfo("完成", "已导入基线数据")
        
    def draw_raw(self):

        if not self.states:
            messagebox.showerror("错误", "未选择有效的脑电信号")
            return
        else:
            current_state = self.states_dropdown.get()
        
        if current_state == "已导入事件！":
            messagebox.showerror("错误", "未选择有效的脑电信号")
            return
        else:
            # 绘制信号，选择要绘制的通道，默认绘制前 10 个通道
            raw_draw =self.states[current_state]
            if current_state == "分割完成！" and type(raw_draw)!= list:
                raw_draw.plot(n_channels=len(raw_draw.ch_names),scalings='auto', title=current_state, show=True)
            elif current_state == "分割完成！" and type(raw_draw)==list:
                mne.io.concatenate_raws(copy.deepcopy(raw_draw)).plot(title=current_state,scalings='auto',remove_dc=True)
            elif current_state == "已完成基线校准！" and type(raw_draw)==list:
                mne.io.concatenate_raws(copy.deepcopy(raw_draw)).plot(title=current_state,scalings='auto',remove_dc=True)
            else:
                raw_draw.plot(n_channels=len(raw_draw.ch_names),scalings='auto', title=current_state, show=True,remove_dc=True)
    def base_alig(self):
        if not self.states:
            messagebox.showerror("错误", "未选择有效的脑电信号")
            return
        else:
            current_state = self.states_dropdown.get()
        
        if current_state == "分割完成！" and self.raw_base_epoch!=None:
            self.base_aligned()
        else:
            messagebox.showerror("错误", "请选择已分段的EEG数据并完成基线数据的导入")
            return
    ############################################后处理##########################################
    def ERSP_Cal(self):
        if "已完成基线校准！" in self.states:
            ERSP_cal(self.__master,self.states["已完成基线校准！"],self.raw_base_epoch)
        else:
            messagebox.showerror("错误", "请完成基线校准后进行ERSP计算！")
            return 
        
    def PSD_Cal(self):
        if not self.states:
            messagebox.showerror("错误", "未选择有效的脑电信号")
            return
        else:
            current_state = self.states_dropdown.get()

        df=compute_power_band(self.states[current_state])
                    # 弹出文件保存对话框
        excel_filename = asksaveasfilename(defaultextension=".xlsx",
                                            filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
                                            title="Save Excel File")
                                            
        if excel_filename:  # 检查用户是否选择了文件名
            # 将 DataFrame 导出为 Excel 文件
            df.to_excel(excel_filename, sheet_name='PSD')

        else:
            messagebox.showerror("Error!","Save operation was canceled.")
        return 
    
    def MLE_Cal(self):
        if not self.states:
            messagebox.showerror("错误", "未选择有效的脑电信号")
            return
        else:
            current_state = self.states_dropdown.get()

        def handle_result(result):
            print("MLE 计算结果：")
            print(result)


        MLE(self.__master,self.states[current_state],handle_result)
 
        return 
    
    def FuzzEn_Cal(self):
        if not self.states:
            messagebox.showerror("错误", "未选择有效的脑电信号")
            return
        else:
            current_state = self.states_dropdown.get()

        df=EEG_FuzzEn(self.states[current_state])
        print(df)
        return 
    
    def PDC_Cal(self):
        if not self.states:
            messagebox.showerror("错误", "未选择有效的脑电信号")
            return
        else:
            current_state = self.states_dropdown.get()

        eeg_pdc(self.__master,self.states[current_state])
        
        return 
    
    def on_closing(self):
        # 关闭程序
        self.__master.quit()
        self.__master.destroy()            