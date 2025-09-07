# EEGlab-Python: 脑电数据处理与分析软件

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)

EEGlab-Python 是一款基于 Python 开发的开源脑电（EEG）信号处理与分析工具，旨在为科研用户提供一个**跨平台、易用、可扩展**的 MATLAB EEGlab 替代方案。支持从数据导入、预处理到时频分析与功能连接计算的完整流程。

## 🌟 功能亮点

- ✅ **多格式支持**：支持  `.bdf`, `.edf`, `.csv` 等常见脑电数据格式导入
- ✅ **完整预处理流程**：带通滤波、工频去噪（50Hz）、ICA 成分自动识别与剔除
- ✅ **高级分析功能**：
  - 时频分析：ERSP（事件相关谱扰动）、PSD（功率谱密度）
  - 非线性动力学：最大李雅普诺夫指数（Max Lyapunov Exponent）
  - 功能连接：PDC（部分定向相干）
- ✅ **可视化与导出**：支持多通道脑电图、时频图、拓扑图可视化，结果可导出为 CSV/PNG

## 🛠 技术栈

- **语言**：Python 3.8+
- **GUI**：Tkinter
- **信号处理**：NumPy, SciPy, MNE-Python
- **可视化**：Matplotlib
- **数据管理**：Pandas

## 🚀 快速开始

### 1. 克隆项目
```bash
git clone https://github.com/mikasa2552/Gait_EMG_EEG_AnalyseSoftware.git
cd Gait_EMG_EEG_AnalyseSoftware

安装依赖
pip install -r requirements.txt
