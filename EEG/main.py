import shutup
shutup.please()
import warnings
# 忽略所有警告
warnings.filterwarnings("ignore",category = UserWarning)
warnings.simplefilter("error")
import logging
# 设置日志级别为WARNING，抑制INFO级别的信息
logging.getLogger('mne').setLevel(logging.WARNING)
import tkinter as tk
from EEGApp.EEGApp import EEGApp

# 运行应用
if __name__ == "__main__":
    root = tk.Tk()
    app = EEGApp(root)
    root.mainloop()
