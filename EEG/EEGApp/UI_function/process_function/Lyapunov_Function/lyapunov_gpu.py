# -*- coding: utf-8 -*-

"""Functions to estimate the maximum Lyapunov exponent.

This module provides two functions to estimate the maximum Lyapunov
exponent (MLE) from a scalar and vector time series.

  * mle -- estimate the MLE from a vector time series
  * mle_embed -- estimate the MLE from a scalar time series after
    reconstruction.
"""

from __future__ import absolute_import, division, print_function

import numpy as np
import torch

from . import utils_gpu
from scipy import signal
import os

# 设置环境变量以减少内存碎片
os.environ['PYTORCH_CUDA_ALLOC_CONF'] = 'expandable_segments:True'

def estimate_memory_usage(n, dtype=torch.float64):
    """
    估计距离矩阵的内存使用量（以 GiB 为单位）。
    """
    # 每个元素占用的字节数
    if dtype == torch.float64:
        bytes_per_element = 8
    elif dtype == torch.float32:
        bytes_per_element = 4
    else:
        raise ValueError("Unsupported dtype")
    
    # 距离矩阵的内存使用量
    memory_usage = (n * n * bytes_per_element) / (1024 ** 3)  # 转换为 GiB
    return memory_usage

def mle_gpu(y, maxt=500, window=10, metric='euclidean', maxnum=None, batch_size=None):
    """
    计算 MLE（最大 Lyapunov 指数），支持分批计算距离矩阵。
    """
    y_tensor = torch.tensor(y, dtype=torch.float64).cuda()
    index, dist = utils_gpu.neighbors_gpu(y_tensor, metric=metric, window=window, maxnum=maxnum)
    m = len(y_tensor)
    maxt = min(m - window - 1, maxt)
    d = torch.empty(maxt, device=y_tensor.device)
    d[0] = torch.mean(torch.log(dist) + 1e-10)

    for t in range(1, maxt):
        t1 = torch.arange(t, m, device=y_tensor.device)
        t2 = index[:-t] + t  # index 已经是 PyTorch 张量
        valid = t2 < m
        t1, t2 = t1[valid], t2[valid]

        if batch_size is None:
            # 直接计算距离矩阵
            dist_matrix = torch.cdist(y_tensor[t1], y_tensor[t2], p=2)
            dist_diag = dist_matrix.diag()  # 提取对角线元素
            d[t] = torch.mean(torch.log(dist_diag + 1e-10))
        else:
            # 分批计算距离矩阵
            dist_diag = []
            for i in range(0, len(t1), batch_size):
                batch_t1 = t1[i:i + batch_size]
                batch_t2 = t2[i:i + batch_size]
                batch_dist_matrix = torch.cdist(y_tensor[batch_t1], y_tensor[batch_t2], p=2)
                dist_diag.append(batch_dist_matrix.diag())
            dist_diag = torch.cat(dist_diag)
            d[t] = torch.mean(torch.log(dist_diag + 1e-10))

        # 释放未使用的内存
        torch.cuda.empty_cache()

    return d.cpu().numpy()

# def mle_embed_gpu(x, dim=[1], tau=1, window=10, maxt=500,
#                   metric='euclidean', maxnum=None, parallel=True):
#     """
#     计算一维时间序列的 MLE（最大 Lyapunov 指数），动态选择是否使用降采样和分批计算。
#     """
#     # 重构相空间
#     yy = [utils_gpu.reconstruct(x, dim=d, tau=tau) for d in dim]

#     # 检查是否需要降采样和分批计算
#     n = len(yy[0])  # 重构后的数据点数
#     estimated_memory = estimate_memory_usage(n)

#     # 获取 GPU 可用内存
#     total_memory = torch.cuda.get_device_properties(0).total_memory / (1024 ** 3)  # 总内存（GiB）
#     allocated_memory = torch.cuda.memory_allocated() / (1024 ** 3)  # 已分配内存（GiB）
#     free_memory = total_memory - allocated_memory  # 可用内存（GiB）

#     if estimated_memory > free_memory:
#         print(f"警告：预计内存使用量 {estimated_memory:.2f} GiB 超过可用内存 {free_memory:.2f} GiB，启用降采样和分批计算。")
#         # 降采样
#         x_downsampled = signal.decimate(x, q=3)  # 降采样到 333 Hz
#         yy = [utils_gpu.reconstruct(x_downsampled, dim=d, tau=tau) for d in dim]
#         # 设置分批大小
#         batch_size = 3000
#     else:
#         batch_size = None

#     # 计算 MLE
#     if parallel:
#         results = [mle_gpu(y, maxt=maxt, window=window, metric=metric, maxnum=maxnum, batch_size=batch_size) for y in yy]
#     else:
#         results = [mle_gpu(y, maxt=maxt, window=window, metric=metric, maxnum=maxnum, batch_size=batch_size) for y in yy]

#     return np.array(results)
def mle_embed_gpu(x, dim=[3], tau=1, window=10, maxt=500,
                 metric='euclidean', maxnum=50, 
                 max_downsample_factor=10, min_batch_size=100,
                 min_signal_length=500):
    """最终稳定版（修复所有已知问题）"""
    # 初始化环境
    torch.backends.cuda.matmul.allow_tf32 = True  # 启用TensorCore加速
    torch.backends.cudnn.benchmark = True        # 自动优化卷积算法
    os.environ['PYTORCH_CUDA_ALLOC_CONF'] = 'expandable_segments:True'  # 防碎片化

    # 重构相空间
    x_phase = [utils_gpu.reconstruct(x.copy(), dim=d, tau=tau) for d in dim]

    # 检查是否需要降采样和分批计算
    n_x_phase = len(x_phase[0])  # 重构后的数据点数
    estimated_memory = estimate_memory_usage(n_x_phase)

    # 单次显存检测
    total_mem = torch.cuda.get_device_properties(0).total_memory / (1024**3)
    initial_free = torch.cuda.mem_get_info()[0] / (1024**3)
    print(f"[系统状态] 显卡总显存: {total_mem:.1f}GiB | 初始可用: {initial_free:.1f}GiB | 预计内存使用量 {estimated_memory:.1f} GiB\n")
    print("━"*40)

    for q in range(1, max_downsample_factor + 1):
        torch.cuda.empty_cache()
        current_free = torch.cuda.mem_get_info()[0] / (1024**3)
        
        try:
            # 降采样处理
            x_processed = signal.decimate(x, q=q, zero_phase=True) if q > 1 else x.copy()
            print(f"[策略] {'降采样' if q>1 else '原始'} q={q} → {len(x_processed)}点 ({1000/max(q,1):.1f}Hz)")

            # 重构相空间
            yy = []
            for d in dim:
                y = utils_gpu.reconstruct(x_processed, dim=d, tau=tau)
                if len(y) < 10:  # 安全检查
                    raise RuntimeError(f"重构后数据不足10点(dim={d})")
                yy.append(y)
            
            # 动态批次计算
            n = len(yy[0])
            elem_size = 8  # float64=8字节
            safe_size = int(current_free * 0.8 * (1024**3) / (n * elem_size))
            batch_size = min(n, max(min_batch_size, safe_size))
            
            print(f"[资源] batch_size={batch_size} (需{round(batch_size*n*elem_size/(1024**3),1)}GiB)")
            

            # 正式计算
            results = []
            for i, y in enumerate(yy):
                print(f"⌛ 维度{dim[i]}计算中...", end=' ', flush=True) 
                res = mle_gpu(y, maxt=maxt, window=window, 
                            metric=metric, maxnum=maxnum,
                            batch_size=batch_size)
                results.append(res)

                torch.cuda.synchronize()  # 确保计算完成
                torch.cuda.empty_cache()  # 强制释放
            print(f"🎉 q={q}, batch_size={batch_size} 成功！")
            print("━"*40)
            return np.array(results)

        except RuntimeError as e:
            err_msg = str(e).split('.')[0]  # 取错误首句
            print(f"⚠️ q={q}失败: {err_msg}")
            if q == max_downsample_factor:
                raise RuntimeError(f"所有降采样尝试失败(最大q={max_downsample_factor})")
            continue

    raise RuntimeError("意外退出循环")  # 理论上不应执行到此处