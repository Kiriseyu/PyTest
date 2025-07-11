# -*- coding: utf-8 -*-
"""
男胎 BMI 分组最早达标孕周 & 六大检验
女胎异常判定模型（Logistic + RandomForest）
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from sklearn.metrics import r2_score, accuracy_score, recall_score, roc_auc_score, classification_report
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.utils import resample
from 决策树最佳时点 import run_survival_timing
from scipy.stats import f_oneway
import statsmodels.api as sm


# ---------------- 独立入口：仅做女胎异常判定 ----------------
def female_abnormality_entry(cleaned_female_path: str, out_dir: str):
    from sklearn.metrics import ConfusionMatrixDisplay
    df = pd.read_excel(Path(cleaned_female_path))
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    feats = ['X染色体的Z值', '13号染色体的Z值', '18号染色体的Z值', '21号染色体的Z值',
             '孕妇BMI', 'GC含量', '唯一比对的读段数']
    # 只删标签缺失，不再删特征缺失
    df = df.dropna(subset=['染色体的非整倍体'])
    X = df[feats].copy()
    y = df['染色体的非整倍体'].apply(lambda x: 0 if str(x).strip() == '' else 1)

    # 简单中位数插补
    X = X.apply(pd.to_numeric, errors='coerce')
    X = X.fillna(X.median())

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.3, random_state=42, stratify=y)

    # Logistic
    lr = LogisticRegression(max_iter=2000)
    lr.fit(X_train, y_train)
    y_pred_lr = lr.predict(X_test)
    print("\n【女胎-Logistic回归】")
    print("准确率:", accuracy_score(y_test, y_pred_lr))
    print("召回率:", recall_score(y_test, y_pred_lr))
    print("AUC   :", roc_auc_score(y_test, y_pred_lr))
    print(classification_report(y_test, y_pred_lr, digits=3))

    # RandomForest
    rf = RandomForestClassifier(n_estimators=500, random_state=42)
    rf.fit(X_train, y_train)
    y_pred_rf = rf.predict(X_test)
    print("\n【女胎-随机森林】")
    print("准确率:", accuracy_score(y_test, y_pred_rf))
    print("召回率:", recall_score(y_test, y_pred_rf))
    print("AUC   :", roc_auc_score(y_test, y_pred_rf))
    print(classification_report(y_test, y_pred_rf, digits=3))

    # 特征重要性
    imp = pd.Series(rf.feature_importances_, index=feats).sort_values(ascending=False)
    print("\n【随机森林特征重要性】")
    print(imp.to_string())

    # 保存
    out_txt = out_dir / "女胎异常判定结果.txt"
    with open(out_txt, 'w', encoding='utf-8') as f:
        f.write("【Logistic回归】\n")
        f.write(f"准确率: {accuracy_score(y_test, y_pred_lr):.3f}\n")
        f.write(f"召回率: {recall_score(y_test, y_pred_lr):.3f}\n")
        f.write(f"AUC   : {roc_auc_score(y_test, y_pred_lr):.3f}\n\n")
        f.write("【随机森林】\n")
        f.write(f"准确率: {accuracy_score(y_test, y_pred_rf):.3f}\n")
        f.write(f"召回率: {recall_score(y_test, y_pred_rf):.3f}\n")
        f.write(f"AUC   : {roc_auc_score(y_test, y_pred_rf):.3f}\n\n")
        f.write("特征重要性（降序）:\n")
        f.write(imp.to_string())
    print("\n✅ 女胎异常判定模型完成，结果已保存至：", out_txt)

    # 混淆矩阵图
    ConfusionMatrixDisplay.from_estimator(rf, X_test, y_test, cmap="Blues")
    plt.title("女胎异常判定-随机森林混淆矩阵")
    plt.savefig(out_dir / "女胎异常判定_混淆矩阵.png")
    plt.close()



# ---------------- 男胎分析器 ----------------
class MaleBMIAnalyzer:
    def __init__(self, cleaned_male_path: Path, out_dir: Path):
        self.df = pd.read_excel(cleaned_male_path)
        self.out_dir = out_dir
        self.out_dir.mkdir(parents=True, exist_ok=True)
        self.bins = [0, 20, 28, 32, 36, 40, 100]
        self.labels = ['<20', '[20,28)', '[28,32)', '[32,36)', '[36,40)', '>=40']
        self.res = None
        print("【男胎Y浓度描述】")
        print(self.df['Y染色体浓度'].describe())
        print("【达标样本数（≥4）】", (self.df['Y染色体浓度'] >= 4).sum())
        print("【达标样本数（≥0.04）】", (self.df['Y染色体浓度'] >= 0.04).sum())

    # ---------------- 核心表：最早达标孕周 + 95%CI ----------------
    def earliest_week_with_ci(self, n_bootstrap=1000):
        self.df['达标'] = self.df['Y染色体浓度'] >= 0.04
        earliest, ci_low, ci_high = {}, {}, {}

        for grp, sub in self.df.groupby(pd.cut(self.df['孕妇BMI'], bins=self.bins, labels=self.labels)):
            达标孕周 = sub[sub['达标']]['检测孕周'].dropna()
            if 达标孕周.empty:
                earliest[grp] = ci_low[grp] = ci_high[grp] = np.nan
                continue
            earliest[grp] = 达标孕周.min()
            boot_stats = [resample(达标孕周).min() for _ in range(n_bootstrap)]
            ci_low[grp] = np.percentile(boot_stats, 2.5)
            ci_high[grp] = np.percentile(boot_stats, 97.5)

        self.res = pd.DataFrame({
            'BMI组': list(earliest.keys()),
            '最早达标孕周': list(earliest.values()),
            'CI_lower': list(ci_low.values()),
            'CI_upper': list(ci_high.values())
        })
        self.res.to_csv(self.out_dir / 'earliest_week.csv', index=False)
        print('[男胎BMI] 最早达标孕周+95%CI：')
        print(self.res)
        return self.res

    # ---------------- 浓度模型 ----------------
    def concentration_model(self):
        from sklearn.linear_model import LinearRegression
        from sklearn.metrics import r2_score
        import statsmodels.api as sm

        df = self.df.dropna(subset=['Y染色体浓度', '检测孕周', '孕妇BMI', '年龄'])
        X = df[['检测孕周', '孕妇BMI', '年龄']]
        y = df['Y染色体浓度']
        X_sm = sm.add_constant(X)
        model = sm.OLS(y, X_sm).fit()
        print(model.summary())
        with open(self.out_dir / '浓度回归模型_summary.txt', 'w', encoding='utf-8') as f:
            f.write(model.summary().as_text())
        lr = LinearRegression()
        lr.fit(X, y)
        print(f"[浓度模型] 线性 R² = {r2_score(y, lr.predict(X)):.3f}")
        return model

    # ---------------- 其余男胎方法 ----------------
    def goodness_of_fit(self):
        lr = LinearRegression()
        X = self.df[['孕妇BMI']].dropna()
        y = self.df.loc[X.index, '检测孕周']
        lr.fit(X, y)
        r2 = r2_score(y, lr.predict(X))
        print(f'[拟合优度] 孕周~BMI 线性 R² = {r2:.3f}')
        with open(self.out_dir / 'goodness_of_fit.txt', 'w', encoding='utf-8') as f:
            f.write(f'R² = {r2}\n')
        return r2

    def group_effect(self):
        from scipy.stats import f_oneway
        groups = [sub[sub['达标']]['检测孕周'].dropna().values
                  for _, sub in self.df.groupby(pd.cut(self.df['孕妇BMI'], bins=self.bins, labels=self.labels))
                  if not sub.empty]
        if len(groups) < 2:
            print('[分组效果] 样本不足，跳过 ANOVA')
            return
        stat, p = f_oneway(*groups)
        print(f'[分组效果] ANOVA F={stat:.2f}, p={p:.3g}')
        with open(self.out_dir / 'group_effect.txt', 'w', encoding='utf-8') as f:
            f.write(f'F={stat}, p={p}\n')
        return p

    def bootstrap_summary(self):
        fig_dir = self.out_dir / 'figs'
        fig_dir.mkdir(parents=True, exist_ok=True)
        sns.histplot([resample(self.df[self.df['达标']]['检测孕周'].dropna()).min()
                      for _ in range(1000)], kde=True)
        plt.title('Bootstrap 最早达标孕周分布')
        plt.savefig(fig_dir / 'bootstrap_dist.png')
        plt.close()

    def reasonability_check(self):
        recommend = self.res.set_index('BMI组')['最早达标孕周']
        reason = {}
        for grp, sub in self.df.groupby(pd.cut(self.df['孕妇BMI'], bins=self.bins, labels=self.labels)):
            达标孕周 = sub[sub['达标']]['检测孕周'].dropna()
            if 达标孕周.empty:
                reason[grp] = '样本不足'
                continue
            pct95 = np.percentile(达标孕周, 95)
            reason[grp] = '合理' if recommend[grp] <= pct95 else '偏早'
        self.res['合理性'] = self.res['BMI组'].map(reason)
        self.res.to_csv(self.out_dir / 'earliest_week.csv', index=False)
        print('[合理性] 检查结果：')
        print(self.res[['BMI组', '合理性']])

    def sensitivity_bmi_cut(self):
        shift = [-1, 0, 1]
        sens = []
        for s in shift:
            bins_s = [b + s for b in self.bins]
            tmp = self.df.copy()
            tmp['grp'] = pd.cut(tmp['孕妇BMI'], bins=bins_s, labels=self.labels)
            for grp, sub in tmp.groupby('grp'):
                达标 = sub[sub['达标']]['检测孕周'].dropna()
                if not 达标.empty:
                    sens.append({'shift': s, 'BMI组': grp, '最早达标': 达标.min()})
        sens_df = pd.DataFrame(sens)
        sens_df.to_csv(self.out_dir / 'sensitivity_bmi_cut.csv', index=False)
        print('[敏感性] BMI 切点±1 结果：')
        print(sens_df.head())

    def perturbation_Y(self, noise_std=0.2):
        n_iter = 500
        perturb_res = []
        for i in range(n_iter):
            tmp = self.df.copy()
            tmp['Y染色体浓度'] *= np.random.normal(1, noise_std, size=len(tmp))
            tmp['达标'] = tmp['Y染色体浓度'] >= 0.04
            for grp, sub in tmp.groupby(pd.cut(tmp['孕妇BMI'], bins=self.bins, labels=self.labels)):
                达标孕周 = sub[sub['达标']]['检测孕周'].dropna()
                if not 达标孕周.empty:
                    perturb_res.append({'iter': i, 'BMI组': grp, '最早达标': 达标孕周.min()})
        if not perturb_res:
            print('[扰动] 无达标样本，跳过扰动分析。')
            return
        pert_df = pd.DataFrame(perturb_res)
        summary = pert_df.groupby('BMI组')['最早达标'].agg(['mean', 'std']).reset_index()
        summary.to_csv(self.out_dir / 'perturbation_summary.csv', index=False)
        print('[扰动] Y 浓度±20 % 最早孕周均值±std：')
        print(summary)

    def survival_best_timing(self):
        csv_path = self.out_dir.parent / 'CleanResult' / '男胎' / 'cleaned_survival_data.csv'
        if not csv_path.exists():
            print('[生存分析] 未找到 cleaned_survival_data.csv，跳过')
            return
        return run_survival_timing(csv_path, self.out_dir / 'survival')

    # ---------------- 一键运行 ----------------
    def run_all(self):
        self.earliest_week_with_ci()
        self.goodness_of_fit()
        self.group_effect()
        self.bootstrap_summary()
        self.reasonability_check()
        self.sensitivity_bmi_cut()
        self.perturbation_Y()
        self.concentration_model()
        self.survival_best_timing()
        print('[男胎BMI] 全部检验完成！')


# ---------------- 男胎入口 ----------------
def male_bmi_best_week_entry(cleaned_male_path: str, out_dir: str):
    analyzer = MaleBMIAnalyzer(Path(cleaned_male_path), Path(out_dir))
    # 浓度分布图已并入 __init__
    analyzer.run_all()