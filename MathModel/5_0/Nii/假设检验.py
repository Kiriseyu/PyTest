import pandas as pd
from scipy import stats

# 读取数据
df = pd.read_excel('数据.xlsx')

# 对年龄、BMI、生产次数进行 t 检验
t_stat_age, p_value_age = stats.ttest_1samp(df['年龄'], 30)  # 假设检验：平均年龄是否等于30
t_stat_bmi, p_value_bmi = stats.ttest_1samp(df['孕妇BMI'], 25)  # 假设检验：BMI 是否为 25

print(f'年龄 t检验结果：t={t_stat_age}, p-value={p_value_age}')
print(f'孕妇BMI t检验结果：t={t_stat_bmi}, p-value={p_value_bmi}')
