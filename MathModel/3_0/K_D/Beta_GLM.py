# coding: utf-8
import os, warnings, joblib, logging, datetime as dt
import pandas as pd, numpy as np, matplotlib.pyplot as plt
import statsmodels.api as sm, statsmodels.formula.api as smf
from patsy import dmatrix
from scipy import stats, special
from sklearn.preprocessing import StandardScaler

# ---------- 环境准备 ----------
os.makedirs("LOG", exist_ok=True)
os.makedirs("PLOT(SimHei)", exist_ok=True)
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False
warnings.filterwarnings('ignore')

TIME_STAMP = dt.datetime.now().strftime('%Y%m%d_%H%M%S')
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f"LOG/model_log_{TIME_STAMP}.txt", encoding='utf-8'),
        logging.StreamHandler()
    ])
logger = logging.getLogger()


# ---------- 工具函数 ----------
def create_spline_basis(df, variable, n_splines=5):
    """返回（basis_matrix, column_names）"""
    formula = f"cr({variable}, df={n_splines})"
    basis = dmatrix(formula, df, return_type='dataframe')
    cols = [f"{variable}_spline{i}" for i in range(basis.shape[1])]
    basis.columns = cols
    return basis, cols


def fit_beta_regression(data, y_var, fix_vars, n_spl=5):
    """使用logit变换和线性回归近似Beta回归"""
    # 对响应变量进行logit变换
    data['logit_y'] = np.log(data[y_var] / (1 - data[y_var] + 1e-8))

    # 准备公式
    formula_terms = []
    for var in fix_vars:
        if data[var].dtype in [np.int64, np.float64]:
            # 对连续变量使用样条基
            basis, cols = create_spline_basis(data, var, n_spl)
            data[cols] = basis
            formula_terms.extend(cols)
        else:
            # 对分类变量使用分类编码
            formula_terms.append(f"C({var})")

    formula = f"logit_y ~ {' + '.join(formula_terms)}"
    logger.info(f"近似Beta回归模型公式: {formula}")

    try:
        # 使用OLS回归
        model = smf.ols(formula, data).fit()
        logger.info("近似Beta回归成功")
        return model, formula_terms
    except Exception as e:
        logger.error(f"回归失败: {e}")
        raise e


# ---------- 诊断图 ----------
def save_diagnostics(model, data, y_var):
    """残差图 + QQ 图"""
    # 计算预测值和残差
    pred = special.expit(model.predict(data))  # 使用expit函数将logit转换回概率
    resid = data[y_var] - pred

    # 残差图
    plt.figure(figsize=(12, 5))
    plt.subplot(1, 2, 1)
    plt.scatter(pred, resid, alpha=.6)
    plt.axhline(0, color='r', ls='--')
    plt.xlabel("拟合值")
    plt.ylabel("残差")
    plt.title("残差图")

    # QQ图
    plt.subplot(1, 2, 2)
    stats.probplot(resid, dist="norm", plot=plt)
    plt.title("QQ图")

    plt.tight_layout()
    plt.savefig(f"PLOT(SimHei)/diagnostics_{TIME_STAMP}.png", dpi=300)
    plt.close()
    logger.info("诊断图已保存")


# ---------- 平滑效应图 ----------
def plot_smooth_effects(model, data, cont_vars, n_spl=5):
    """绘制连续变量的平滑效应"""
    y_var = "Y染色体浓度"
    for var_name in cont_vars:
        if data[var_name].dtype in [np.int64, np.float64]:
            # 创建预测网格
            x_grid = np.linspace(data[var_name].min(), data[var_name].max(), 100)
            pred_data = pd.DataFrame({
                var_name: x_grid
            })

            # 为其他变量设置均值或众数
            for other_var in data.columns:
                if other_var != var_name and other_var in model.model.exog_names:
                    if data[other_var].dtype in [np.int64, np.float64]:
                        pred_data[other_var] = data[other_var].mean()
                    else:
                        pred_data[other_var] = data[other_var].mode()[0]

            # 生成样条基（如果需要）
            if any([col.startswith(f"{var_name}_spline") for col in model.model.exog_names]):
                basis, cols = create_spline_basis(pred_data, var_name, n_spl)
                for col in cols:
                    pred_data[col] = basis[col]

            # 预测
            pred_data['logit_pred'] = model.predict(pred_data)
            pred_data['pred'] = special.expit(pred_data['logit_pred'])  # 转换回概率

            # 绘制图形
            plt.figure(figsize=(8, 5))
            plt.plot(pred_data[var_name], pred_data['pred'], color='blue', linewidth=2)
            plt.scatter(data[var_name], data[y_var], alpha=0.3, color='gray')
            plt.xlabel(var_name)
            plt.ylabel("预测Y染色体浓度")
            plt.title(f"{var_name}对Y染色体浓度的平滑效应")
            plt.tight_layout()
            plt.savefig(f"PLOT(SimHei)/smooth_{var_name}_{TIME_STAMP}.png", dpi=300)
            plt.close()
            logger.info(f"{var_name}平滑效应图已保存")


# ---------- 变量重要性 ----------
def save_importance(model):
    """计算并保存变量重要性"""
    if not hasattr(model, 'pvalues'):
        logger.warning("模型无pvalues，跳过重要性图")
        return

    # 计算重要性（使用1/p值）
    imp = 1 / model.pvalues
    imp_df = (imp.to_frame(name='重要性')
              .reset_index()
              .rename(columns={'index': '变量'})
              .sort_values('重要性', ascending=False))

    # 过滤掉截距项
    imp_df = imp_df[~imp_df['变量'].str.contains('Intercept')]

    plt.figure(figsize=(10, 8))
    plt.barh(imp_df['变量'], imp_df['重要性'])
    plt.xlabel("1/p值")
    plt.title("变量重要性")
    plt.tight_layout()
    plt.savefig(f"PLOT(SimHei)/importance_{TIME_STAMP}.png", dpi=300)
    plt.close()
    logger.info("变量重要性图已保存")


# ---------- 主流程 ----------
def main():
    # 1. 数据加载与预处理
    data = pd.read_excel("CL/cleaned_data.xlsx")
    logger.info(f"数据读取完成：{data.shape[0]}行 × {data.shape[1]}列")

    # 筛选男胎数据（Y染色体浓度非空）
    male_data = data[data['Y染色体浓度'].notna()].copy()
    logger.info(f"男胎数据：{male_data.shape[0]}行")

    # 2. 变量定义
    y_var = "Y染色体浓度"
    # 根据问题1，重点关注孕周数和BMI，同时考虑其他可能影响因素
    fix_vars = ["年龄", "身高", "体重", "检测孕周", "孕妇BMI", "GC含量"]

    # 3. 数据标准化（对连续变量）
    cont_vars = [var for var in fix_vars if male_data[var].dtype in [np.int64, np.float64]]
    scaler = StandardScaler()
    male_data[cont_vars] = scaler.fit_transform(male_data[cont_vars])

    # 4. 建模
    model, formula_terms = fit_beta_regression(male_data, y_var, fix_vars)

    # 5. 模型摘要
    with open(f"LOG/model_summary_{TIME_STAMP}.txt", "w", encoding='utf-8') as f:
        f.write("近似Beta回归模型摘要（使用logit变换和OLS）\n")
        f.write("=" * 50 + "\n")
        f.write(model.summary().as_text())
        f.write("\n\n模型显著性检验:\n")
        f.write(f"F检验p值: {model.f_pvalue}\n")
        f.write(f"R²: {model.rsquared}\n")
        f.write(f"调整R²: {model.rsquared_adj}\n")
        f.write(f"AIC: {model.aic}\n")
        f.write(f"BIC: {model.bic}\n")

    logger.info("模型摘要已写入LOG")

    # 6. 预测与残差计算
    predictions = male_data.copy()
    predictions['logit_fitted'] = model.fittedvalues
    predictions['fitted'] = special.expit(model.fittedvalues)  # 转换回概率
    predictions['residual'] = male_data[y_var] - predictions['fitted']

    # 保存预测结果
    pred_file = f"CL/predictions_{TIME_STAMP}.xlsx"
    predictions.to_excel(pred_file, index=False)
    logger.info(f"预测结果已保存至: {pred_file}")

    # 7. 诊断与可视化
    save_diagnostics(model, male_data, y_var)

    # 绘制连续变量的平滑效应
    plot_smooth_effects(model, male_data, cont_vars)

    # 变量重要性
    save_importance(model)

    # 8. 模型持久化
    model_file = f"CL/beta_model_{TIME_STAMP}.pkl"
    joblib.dump(model, model_file)
    logger.info(f"模型已保存至: {model_file}")

    # 9. 输出关键结果
    logger.info("=" * 50)
    logger.info("问题1关键结果:")

    # 提取与孕周和BMI相关的p值
    week_pvals = [model.pvalues.get(col, np.nan) for col in model.pvalues.index if '检测孕周' in col]
    bmi_pvals = [model.pvalues.get(col, np.nan) for col in model.pvalues.index if '孕妇BMI' in col]

    logger.info(f"Y染色体浓度与孕周数的关系: 最小p值 = {np.nanmin(week_pvals) if len(week_pvals) > 0 else 'N/A'}")
    logger.info(f"Y染色体浓度与BMI的关系: 最小p值 = {np.nanmin(bmi_pvals) if len(bmi_pvals) > 0 else 'N/A'}")
    logger.info(f"模型整体显著性: F检验p值 = {model.f_pvalue}")
    logger.info(f"模型解释方差: R² = {model.rsquared:.4f}")
    logger.info("=" * 50)


if __name__ == "__main__":
    main()