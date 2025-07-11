# zscore_fix.py
import pandas as pd
import numpy as np
from pathlib import Path
import datetime

# ------------- 路径 -------------
SRC_FILE = Path(r'C:\Users\26790\Desktop\单步处理\附件_1.1_data.xlsx')
OUT_DIR  = Path(r'C:\Users\26790\Desktop\Result\AnalysisResult')
LOG_DIR  = Path(r'C:\Users\26790\Desktop\CleanedLog')

OUT_FILE = OUT_DIR / '附件_1.1_zscore.xlsx'
LOG_FILE = LOG_DIR / 'zscore_log.txt'

OUT_DIR.mkdir(parents=True, exist_ok=True)
LOG_DIR.mkdir(parents=True, exist_ok=True)

def _write_log(lines):
    with LOG_FILE.open('a', encoding='utf-8') as f:
        f.write('\n'.join(lines) + '\n')

def str2floats(cell):

    if pd.isna(cell):
        return []
    # 1. 已经是数值类型
    if isinstance(cell, (int, float)):
        return [float(cell)]
    # 2. 字符串处理
    s = str(cell).strip().replace('＋', '+').replace('W', 'w')
    if 'w+' in s and len(s.split('w+')) == 2:
        try:
            week, day = s.split('w+')
            return [float(week) + float(day) / 7]
        except:
            return []
    # 纯数字文本
    try:
        return [float(s)]
    except:
        return []

def main():
    log_lines = [f"{datetime.datetime.now():%F %T} 开始处理"]
    try:
        df = pd.read_excel(SRC_FILE)
    except Exception as e:
        log_lines.append(f"读文件失败：{e}")
        _write_log(log_lines)
        return

    target_cols = ['检测孕周', '孕妇BMI', '年龄','生产次数']
    exist_cols  = [c for c in target_cols if c in df.columns]
    if not exist_cols:
        log_lines.append("目标列均不存在，跳过标准化")
        _write_log(log_lines)
        return

    modified = False
    for col in exist_cols:
        # 1. 拆串 -> 一维列表
        all_nums = []
        for raw in df[col].dropna():
            all_nums.extend(str2floats(raw))

        if not all_nums:
            log_lines.append(f"{col} 无有效数值，跳过")
            continue

        # 2. 计算均值、标准差
        mean_val = np.mean(all_nums)
        std_val  = np.std(all_nums, ddof=0)
        if std_val == 0:
            log_lines.append(f"{col} 标准差为 0，跳过")
            continue

        # 3. 把原格子的值逐个标准化，结果仍放 list
        df[f'{col}_z'] = df[col].map(
            lambda x: " ".join([f"{(v - mean_val) / std_val:.6f}" for v in str2floats(x)])
            if pd.notna(x) else np.nan
        )
        modified = True
        log_lines.append(f"{col} 已标准化 → {col}_z（共 {len(all_nums)} 个数值）")

    if modified:
        df.to_excel(OUT_FILE, index=False)
        log_lines.append(f"已保存：{OUT_FILE}")
    else:
        log_lines.append("无可标准化列")

    _write_log(log_lines)

if __name__ == '__main__':
    main()