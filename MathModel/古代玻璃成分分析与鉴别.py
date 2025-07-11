# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegressionCV
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from scipy.stats import mannwhitneyu

plt.rcParams['font.sans-serif'] = ['SimHei']  # 黑体
plt.rcParams['axes.unicode_minus'] = False
# ---------- 工具 ----------
def norm100(df):
    return df.div(df.sum(axis=1), axis=0) * 100

def clr(df):
    eps = 1e-6
    df = df.replace(0, eps)
    g = np.exp(np.log(df).mean(axis=1))
    return np.log(df.div(g, axis=0))

# ---------- 1. 读取 & 统一列名 ----------
# 训练集
train_file = 'Cleaned.xlsx'
train = pd.read_excel(train_file)

# 未知集
unknown_file = '表单3.xlsx'
unknown = pd.read_excel(unknown_file)

# 统一列名：给未知集补前缀
rename_map = {c: f'质量分数_{c}' for c in unknown.columns if c.startswith('氧化') or c in ['二氧化硅(SiO2)','五氧化二磷(P2O5)','二氧化硫(SO2)']}
unknown = unknown.rename(columns=rename_map)

# 成分列
comp_cols = [c for c in train.columns if c.startswith('质量分数_')]

# ---------- 2. 闭合检查 + 填补 + 归一化 ----------
for df in [train, unknown]:
    df[comp_cols] = df[comp_cols].fillna(0)                         # 1. 填 0
    df[comp_cols] = norm100(df[comp_cols])                          # 2. 归一到 100 %
    sums = df[comp_cols].sum(axis=1)
    df = df[(sums >= 85) & (sums <= 105)].copy()                    # 3. 闭合 85–105 %
    df[comp_cols] = SimpleImputer(strategy='mean').fit_transform(df[comp_cols])  # 4. 再次均值填补

# ---------- 3. 问题 1：风化差异 ----------
weather = train['表面风化'].map({'无风化': '未风化', '风化': '风化'})
diff_df = pd.DataFrame(index=comp_cols, columns=['mean_diff', 'p'])
for col in comp_cols:
    a, b = train.loc[weather == '未风化', col], train.loc[weather == '风化', col]
    diff_df.loc[col, 'mean_diff'] = a.mean() - b.mean()
    diff_df.loc[col, 'p'] = mannwhitneyu(a, b, alternative='two-sided')[1]
diff_df['sig'] = diff_df['p'] < 0.05
print('问题1 风化差异显著成分：')
print(diff_df[diff_df['sig']].sort_values('mean_diff'))

# ---------- 4. 问题 2：主分类 + 亚类 ----------
X_clr = clr(train[comp_cols])
clf = LogisticRegressionCV(cv=5, max_iter=1000).fit(X_clr, train['类型'])
train['亚类'] = -1
for glass in ['高钾', '铅钡']:
    mask = train['类型'] == glass
    km = KMeans(n_clusters=3, random_state=0).fit(X_clr[mask])
    train.loc[mask, '亚类'] = km.labels_
    print(f'{glass} 亚类轮廓系数：{silhouette_score(X_clr[mask], km.labels_):.3f}')

# ---------- 5. 问题 3：未知集鉴别 ----------
X_u_clr = clr(unknown[comp_cols])
unknown['预测类型'] = clf.predict(X_u_clr)
unknown['概率'] = clf.predict_proba(X_u_clr).max(axis=1)
unknown.to_excel('未知类别预测结果.xlsx', index=False)
print('问题3 结果已保存：未知类别预测结果.xlsx')

# ---------- 6. 问题 4：成分相关差异 ----------
corr_high = X_clr[train['类型'] == '高钾'].corr()
corr_lead = X_clr[train['类型'] == '铅钡'].corr()
diff_corr = corr_high - corr_lead

plt.figure(figsize=(8, 6))
sns.heatmap(diff_corr, cmap='coolwarm', center=0)
plt.title('高钾 vs 铅钡 成分相关差异')
plt.tight_layout()
plt.savefig('相关差异热力图.png', dpi=300)
plt.show()

print('全部任务完成！')