# 初始化目录和日志
def s_d():
    os.makedirs("LOG", exist_ok=True)  # 创建LOG目录
    os.makedirs("PLOT(SimHei)", exist_ok=True)  # 创建图像目录
def s_l():
    TIME_STAMP = dt.datetime.now().strftime('%Y%m%d_%H%M%S')  # 获取时间戳
    logging.basicConfig(
        level=logging.INFO,  # 设置日志级别
        format='%(asctime)s - %(levelname)s - %(message)s',  # 日志格式
        handlers=[
            logging.FileHandler(f"LOG/model_log_{TIME_STAMP}.txt", encoding='utf-8'),  # 日志文件
            logging.StreamHandler()  # 控制台日志
        ])
    return logging.getLogger()  # 返回日志记录器
logger = s_l()  # 获取日志记录器
s_d()  # 初始化目录
# 创建样条基
def c_s_b(df, variable, n_splines=5):
    formula = f"cr({variable}, df={n_splines})"  # 样条基公式
    basis = dmatrix(formula, df, return_type='dataframe')  # 样条基矩阵
    basis.columns = [f"{variable}_spline{i}" for i in range(basis.shape[1])]  # 命名列
    return basis  # 返回样条基
# 数据预处理：标准化和样条基
def p_d(data, fix_vars, n_spl=5):
    formula_terms = []  # 存储回归公式项
    for var in fix_vars:
        if data[var].dtype in [np.int64, np.float64]:  # 数值型变量
            basis = c_s_b(data, var, n_spl)  # 创建样条基
            data[basis.columns] = basis  # 添加到数据
            formula_terms.extend(basis.columns)  # 加入公式项
        else:
            formula_terms.append(f"C({var})")  # 类别型变量
    return data, formula_terms  # 返回处理后的数据和公式项
# 拟合Beta回归
def f_b_r(data, y_var, fix_vars, n_spl=5):
    data, formula_terms = p_d(data, fix_vars, n_spl)  # 数据预处理
    data['logit_y'] = np.log(data[y_var] / (1 - data[y_var] + 1e-8))  # logit变换
    formula = f"logit_y ~ {' + '.join(formula_terms)}"  # 回归公式
    logger.info(f"近似Beta回归模型公式: {formula}")  # 日志输出
    try:
        model = smf.ols(formula, data).fit()  # 拟合OLS模型
        logger.info("近似Beta回归成功")  # 拟合成功
        return model, formula_terms  # 返回模型和公式项
    except Exception as e:
        logger.error(f"回归失败: {e}")  # 拟合失败
        raise e
# 保存并绘制诊断图
def s_dg(model, data, y_var):
    pred = special.expit(model.predict(data))  # 预测值
    resid = data[y_var] - pred  # 残差
    p_dg(resid, pred)  # 绘制诊断图
# 绘制诊断图：残差图和QQ图
def p_dg(resid, pred):
    plt.figure(figsize=(12, 5))  # 图像大小
    plt.subplot(1, 2, 1)  # 残差图
    plt.scatter(pred, resid, alpha=.6)  # 拟合值与残差散点
    plt.axhline(0, color='r', ls='--')  # 参考线
    plt.xlabel("拟合值")  # X轴标签
    plt.ylabel("残差")  # Y轴标签
    plt.title("残差图")  # 标题
    plt.subplot(1, 2, 2)  # QQ图
    stats.probplot(resid, dist="norm", plot=plt)  # QQ图
    plt.title("QQ图")  # 标题
    plt.tight_layout()  # 自动调整布局
    plt.savefig(f"PLOT(SimHei)/diagnostics_{TIME_STAMP}.png", dpi=300)  # 保存图像
    plt.close()  # 关闭图像
# 绘制平滑效应图
def p_s_e(model, data, cont_vars):
    for var_name in cont_vars:
        p_s(var_name, model, data)  # 绘制每个变量的平滑效应图
# 绘制单个变量的平滑效应
def p_s(var_name, model, data):
    x_grid = np.linspace(data[var_name].min(), data[var_name].max(), 100)  # 生成自变量网格
    pred_data = pd.DataFrame({var_name: x_grid})  # 创建数据框
    s_o_v(pred_data, var_name, data, model)  # 设置其他变量值
    if any([col.startswith(f"{var_name}_spline") for col in model.model.exog_names]):  # 有样条基
        basis = c_s_b(pred_data, var_name)  # 创建样条基
        pred_data[basis.columns] = basis  # 添加到数据框
    pred_data['logit_pred'] = model.predict(pred_data)  # 预测logit值
    pred_data['pred'] = special.expit(pred_data['logit_pred'])  # 转换为概率
    plt.figure(figsize=(8, 5))  # 图像大小
    plt.plot(pred_data[var_name], pred_data['pred'], color='blue', linewidth=2)  # 绘制平滑曲线
    plt.scatter(data[var_name], data['Y染色体浓度'], alpha=0.3, color='gray')  # 绘制散点
    plt.xlabel(var_name)  # X轴标签
    plt.ylabel("预测Y染色体浓度")  # Y轴标签
    plt.title(f"{var_name}对Y染色体浓度的平滑效应")  # 图标题
    plt.tight_layout()  # 自动调整布局
    plt.savefig(f"PLOT(SimHei)/smooth_{var_name}_{TIME_STAMP}.png", dpi=300)  # 保存图像
    plt.close()  # 关闭图像
# 设置其他变量默认值
def s_o_v(pred_data, var_name, data, model):
    for other_var in data.columns:
        if other_var != var_name and other_var in model.model.exog_names:  # 如果是模型中的其他变量
            pred_data[other_var] = data[other_var].mean() if data[other_var].dtype in [np.int64, np.float64] else \
            data[other_var].mode()[0]  # 设置为均值或众数
# 保存变量重要性图
def s_i(model):
    if hasattr(model, 'pvalues'):  # 检查模型是否有p值
        imp_df = c_i(model)  # 计算重要性
        p_i(imp_df)  # 绘制重要性图
# 计算每个变量的重要性
def c_i(model):
    imp = 1 / model.pvalues  # 重要性为1/p值
    imp_df = imp.to_frame(name='重要性').reset_index().rename(columns={'index': '变量'}).sort_values('重要性',
                                                                                                     ascending=False)  # 创建数据框
    return imp_df[~imp_df['变量'].str.contains('Intercept')]  # 去除截距项
# 绘制变量重要性图
def p_i(imp_df):
    plt.figure(figsize=(10, 8))  # 图像大小
    plt.barh(imp_df['变量'], imp_df['重要性'])  # 绘制水平条形图
    plt.xlabel("1/p值")  # X轴标签
    plt.title("变量重要性")  # 图标题
    plt.tight_layout()  # 自动调整布局
    plt.savefig(f"PLOT(SimHei)/importance_{TIME_STAMP}.png", dpi=300)  # 保存图像
    plt.close()  # 关闭图像
# 主函数，执行分析流程
def main():
    data = pd.read_excel("CL/cleaned_data.xlsx")  # 读取数据
    logger.info(f"数据读取完成：{data.shape[0]}行 × {data.shape[1]}列")  # 输出数据维度
    male_data = data[data['Y染色体浓度'].notna()].copy()  # 筛选出有Y染色体浓度的数据
    logger.info(f"男胎数据：{male_data.shape[0]}行")  # 输出数据行数
    fix_vars = ["年龄", "身高", "体重", "检测孕周", "孕妇BMI", "GC含量"]  # 固定变量
    cont_vars = [var for var in fix_vars if male_data[var].dtype in [np.int64, np.float64]]  # 连续变量
    male_data[cont_vars] = StandardScaler().fit_transform(male_data[cont_vars])  # 标准化数据
    model, formula_terms = f_b_r(male_data, "Y染色体浓度", fix_vars)  # 拟合Beta回归模型
    s_ms(model)  # 保存模型摘要
    s_p(model, male_data)  # 保存预测结果
    s_dg(model, male_data, "Y染色体浓度")  # 保存诊断图
    p_s_e(model, male_data, cont_vars)  # 绘制平滑效应图
    s_i(model)  # 保存变量重要性图
    s_m(model)  # 保存模型
# 保存模型摘要
def s_ms(model):
    with open(f"LOG/model_summary_{TIME_STAMP}.txt", "w", encoding='utf-8') as f:
        f.write(model.summary().as_text())  # 保存模型摘要
# 保存预测结果
def s_p(model, data):
    predictions = data.copy()  # 复制数据
    predictions['logit_fitted'] = model.fittedvalues  # 添加拟合logit值
    predictions['fitted'] = special.expit(model.fittedvalues)  # 转换为概率值
    predictions['residual'] = data['Y染色体浓度'] - predictions['fitted']  # 残差
    predictions.to_excel(f"CL/predictions_{TIME_STAMP}.xlsx", index=False)  # 保存预测结果
# 保存最终模型
def s_m(model):
    model_file = f"CL/beta_model_{TIME_STAMP}.pkl"  # 模型文件名
    joblib.dump(model, model_file)  # 保存模型
    logger.info(f"模型已保存至: {model_file}")  # 输出日志
if __name__ == "__main__":
    main()  # 执行主函数