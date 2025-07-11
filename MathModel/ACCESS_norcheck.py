# normality_check_cn.py
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from scipy import stats
import datetime
import warnings
warnings.filterwarnings("ignore")

# ------------- 路径配置 -------------
SRC_FILE = Path(r'C:\Users\26790\Desktop\单步处理\附件_1.1_2_norcheck.xlsx')
LOG_DIR  = Path(r'C:\Users\26790\Desktop\CleanedLog')
PIC_DIR  = Path(r'C:\Users\26790\Desktop\Result\Plotting')   # 新目录

LOG_FILE = LOG_DIR / 'normality_log.txt'
PIC_DIR.mkdir(parents=True, exist_ok=True)
LOG_DIR.mkdir(parents=True, exist_ok=True)

# ------------- 中文字体 -------------
plt.rcParams['font.family'] = 'SimHei'
plt.rcParams['axes.unicode_minus'] = False

def _write_log(lines):
    with LOG_FILE.open('a', encoding='utf-8') as f:
        f.write('\n'.join(lines) + '\n')

def choose_test(x):
    """Shapiro-Wilk / Lilliefors 根据样本量"""
    n = len(x)
    if n <= 5000:
        return stats.shapiro(x)
    else:
        from statsmodels.stats.diagnostic import lilliefors
        return lilliefors(x)

def plot_qq(col, x, pic_path):
    """直方图 + Q-Q 图（中文标题）"""
    fig, ax = plt.subplots(1, 2, figsize=(10, 4))
    sns.histplot(x, kde=True, ax=ax[0])
    ax[0].set_title(f'{col} 直方图')
    stats.probplot(x, dist="norm", plot=ax[1])
    ax[1].set_title(f'{col} Q-Q 图')
    fig.savefig(pic_path, dpi=300, bbox_inches='tight')
    plt.close(fig)

def str2floats(cell):
    """统一返回 List[float]"""
    if pd.isna(cell):
        return []
    if isinstance(cell, (int, float)):
        return [float(cell)]
    s = str(cell).strip().replace('＋', '+').replace('W', 'w')
    if 'w+' in s and len(s.split('w+')) == 2:
        try:
            week, day = s.split('w+')
            return [float(week) + float(day) / 7]
        except:
            return []
    try:
        return [float(x) for x in s.split()]
    except:
        return []

def main():
    log_lines = [f"{datetime.datetime.now():%F %T} 开始正态性检验"]
    try:
        df = pd.read_excel(SRC_FILE)
    except Exception as e:
        log_lines.append(f"读文件失败：{e}")
        _write_log(log_lines)
        return

    target_cols = ['年龄', '孕妇BMI', '检测孕周', 'Y染色体浓度', '生产次数']
    exist_cols  = [c for c in target_cols if c in df.columns]
    if not exist_cols:
        log_lines.append("目标列均不存在，跳过检验")
        _write_log(log_lines)
        return

    for col in exist_cols:
        all_nums = []
        for raw in df[col].dropna():
            all_nums.extend(str2floats(raw))

        if len(all_nums) < 8:
            log_lines.append(f"{col} 有效样本不足，跳过")
            continue

        stat, p = choose_test(np.array(all_nums))
        normal = "是" if p > 0.05 else "否"

        # 大样本 p≈0 时打印更精确值
        if p == 0:
            p_approx = np.exp(-9.5 * (stat - 1) ** 2 * len(all_nums))
            log_msg = f"{col}  W={stat:.6f}  p≈{p_approx:.2e}  正态={normal}  （真实 p < 1e-18）"
        else:
            log_msg = f"{col}  W={stat:.6f}  p={p:.6f}  正态={normal}"

        log_lines.append(log_msg)
        print(log_msg)

        plot_qq(col, np.array(all_nums), PIC_DIR / f"{col}_qq.png")

    log_lines.append(">>> 图形已保存至：" + str(PIC_DIR))
    _write_log(log_lines)
    print(">>> 日志已保存：" + str(LOG_FILE))

if __name__ == '__main__':
    main()