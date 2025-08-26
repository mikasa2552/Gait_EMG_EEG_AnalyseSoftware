import numpy as np
import matplotlib.pyplot as plt
from nilearn import plotting
import warnings
warnings.filterwarnings("ignore")
import pandas as pd


df_PDC = pd.read_excel(r"E:\学习\2025会议\pdc for healthy and pd.xlsx", index_col=0, header=0,sheet_name='pd') #PDC excel, change sheet name

# 提取通道名称列表（第一列的索引）
channel_labels= df_PDC.index.tolist()

# 提取PDC矩阵（二维数组）
pdc_matrix = df_PDC.values

file_path = r'EEGApp\UI_function\process_function\10-10channels_loc.xlsx'  # channel location excel
df = pd.read_excel(file_path)

# 处理坐标数据：只保留前面的数值
for col in ['X(mm)','Y(mm)','Z(mm)']:
    df[col] = df[col].str.split('±').str[0].astype(float)


# 构建 n * 3 的矩阵
coordinates_matrix = np.zeros((len(channel_labels), 3))  # 初始化矩阵

# 将 Excel 中的 Labels 列转换为大写，以便不区分大小写匹配
df['Labels'] = df['Labels'].str.upper()

# 遍历通道名称列表
for i, ch_name in enumerate(channel_labels):
    # 将通道名称转换为大写
    ch_name_upper = ch_name.upper()
    
    # 找到通道对应的坐标
    if ch_name_upper in df['Labels'].values:
        row = df[df['Labels'] == ch_name_upper]
        coordinates_matrix[i] = row[['X(mm)','Y(mm)','Z(mm)']].values[0]
    else:
        print(f"警告：通道 {ch_name} 未找到对应的坐标！")  

view=plotting.view_connectome(adjacency_matrix=pdc_matrix ,
        node_coords=coordinates_matrix,
        edge_cmap= 'Reds',          # color
        edge_threshold=0, 
        node_size=8,
        linewidth=8,
        title=(f'Brain Connectivity Map (PDC) of PD'),
        symmetric_cmap=False
        )
view.open_in_browser()  
plt.figure()
plotting.plot_connectome(
            adjacency_matrix=pdc_matrix,
            node_coords=coordinates_matrix,
            #node_color = '#00CCCC',
            node_size = 20,
            edge_threshold=0,  
            edge_vmin=0,
            edge_vmax=pdc_matrix.max(),
            edge_cmap='rainbow',
            colorbar=True,
            edge_kwargs={'linewidth': 0.8},
            title=(f'Brain Connectivity Map (PDC) of PD'),
            display_mode='ortho', 
            axes=plt.gca() 
        )
plt.show()