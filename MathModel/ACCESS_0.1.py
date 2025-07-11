import pandas as pd
from pathlib import Path

# ------------ 配置 ------------
SRC_FILE = r'C:\Users\26790\Desktop\BoxFilesPic\附件.xlsx'
DST_DIR  = r'C:\Users\26790\Desktop\Result\AnalysisResult'
DST_FILE = Path(DST_DIR) / '附件_孕周格式修改.xlsx'

# ------------ 转换逻辑（修复版） ------------
def convert_week_str(s):
    if pd.isna(s):
        return s
    s = str(s).replace('＋', '+').replace('W', 'w').strip()

    # 情形1：周+天
    if 'w+' in s and len(s.split('w+')) == 2:
        try:
            week, day = s.split('w+')
            return f"{int(week)}.{int(day) * 10**6 // 7:06d}"
        except:
            return s

    # 情形2：纯周
    if s.endswith('w'):
        try:
            return f"{int(s[:-1])}.000000"
        except:
            return s

    # 情形3：已有纯数字或无法解析
    return s

# ------------ 主流程 ------------
def main():
    Path(DST_DIR).mkdir(parents=True, exist_ok=True)
    with pd.ExcelWriter(DST_FILE, engine='openpyxl') as writer:
        for sheet in ['男胎检测数据', '女胎检测数据']:
            df = pd.read_excel(SRC_FILE, sheet_name=sheet)
            if '检测孕周' in df.columns:
                df['检测孕周'] = df['检测孕周'].apply(convert_week_str)
            df.to_excel(writer, sheet_name=sheet, index=False)
    print(f'>>> 新格式文件已保存至：{DST_FILE}')

if __name__ == '__main__':
    main()