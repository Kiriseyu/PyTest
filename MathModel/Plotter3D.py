import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

# 设置字体为支持中文的字体
plt.rcParams['font.family'] = 'Microsoft YaHei'
plt.rcParams['axes.unicode_minus'] = False

# ------------ 路径 ------------
READ_DIR = Path(r'C:\Users\26790\Desktop\BoxFilesPic')
SAVE_DIR = Path(r'C:\Users\26790\Desktop\Result\Plotting')
SAVE_DIR.mkdir(parents=True, exist_ok=True)

# 主逻辑
for file in READ_DIR.glob('*.xlsx'):
    df = pd.read_excel(file)

    # 你的三列
    X_COL = '作物名称'
    Y_COL = '亩产量/斤'
    Z_COL = '地块面积/亩'

    fig = plt.figure(figsize=(12, 8))
    ax = fig.add_subplot(111, projection='3d')

    # 创建 3D 柱状图
    xpos = np.arange(len(df[X_COL]))
    ypos = df[Y_COL]
    zpos = np.zeros(len(df))

    dx = np.ones(len(df)) * 0.5
    dy = np.ones(len(df)) * 0.5
    dz = df[Z_COL]

    # 使用 colormap
    cmap = plt.cm.get_cmap('viridis')
    colors = cmap(dz / dz.max())

    ax.bar3d(xpos, ypos, zpos, dx, dy, dz, color=colors, zsort='average')

    # 设置标签
    ax.set_xlabel('农作物种类')
    ax.set_ylabel('农作物产量')
    ax.set_zlabel('面积 (亩)')

    # 设置刻度
    ax.set_xticks(xpos)
    ax.set_xticklabels(df[X_COL], rotation=45, ha='right')

    # 设置标题
    ax.set_title(f'{file.stem} 3D 柱状图')

    # 保存图像
    save_path = SAVE_DIR / f'3d_bar_{file.stem}.png'
    plt.tight_layout()
    plt.savefig(save_path, dpi=300)
    plt.close()
    print(f"已保存 → {save_path}")