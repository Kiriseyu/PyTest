from pathlib import Path
from nipt_core import PathConfig, DataCleaner, Analyzer, Plotter, MaleBMIAnalyzer, onna_bunrui_cv

def shuyou():
    SRC_DIR = Path('./')
    RESULT = Path('./Result/AnalysisResult')
    CLEANED = Path('./Result/CleanResult')
    PLOTS = Path('./Result/Plots')
    LOGS = Path('./Result/CleanedLog')

    cfg = PathConfig(SRC_DIR, RESULT, CLEANED, PLOTS, LOGS)
    cfg.ensure()

    cleaner = DataCleaner(cfg, 文件名='附件.xlsx', 男胎表='男胎检测数据', 女胎表='女胎检测数据')
    df_dict = cleaner.jikkou_subete(
        zscore_retsu=['检测孕周', '孕妇BMI', '年龄', '生产次数'],
        kromu_z_retsu=['13号染色体的Z值', '18号染色体的Z值', '21号染色体的Z值', 'X染色体的Z值', 'Y染色体的Z值']
    )
    print('\n✅ 数据清洗完成')

    analyzer = Analyzer(cfg.kk_dr, cfg.log_dir)
    for sheet, df in df_dict.items():
        seibetsu = '男胎' if '男' in sheet else '女胎'
        print(f'\n===== 开始分析 {seibetsu} =====')
        if seibetsu == '男胎':
            analyzer.soukan_bunseki(df[['检测孕周', '孕妇BMI', '年龄', '生产次数', 'Y染色体浓度']], seibetsu)
            analyzer.vif_bunseki(df, ['检测孕周', '孕妇BMI', '年龄', '生产次数'], seibetsu)
            analyzer.ols_kouzou(df, 'Y染色体浓度', ['检测孕周', '孕妇BMI', '年龄', '生产次数'], seibetsu)
            analyzer.mixedlm_jikkou(df, 'Y染色体浓度', ['检测孕周', '孕妇BMI'], '孕妇代码', seibetsu)
        else:
            analyzer.soukan_bunseki(df[['X染色体的Z值', '13号染色体的Z值', '18号染色体的Z值', '21号染色体的Z值', '孕妇BMI', 'GC含量']], seibetsu)

    plotter = Plotter(cfg.zu_dr, tsuyo=True)
    male_df = df_dict.get('男胎检测数据')
    if male_df is not None:
        plotter.histo_zu(male_df, '检测孕周', '男胎_孕周分布.png', '男胎')
        plotter.santen_zu(male_df, '检测孕周', 'Y染色体浓度', '男胎_孕周_vs_Y.png', '男胎')
        plotter.santen_zu(male_df, '孕妇BMI', 'Y染色体浓度', '男胎_BMI_vs_Y.png', '男胎')
    print('\n✅ 绘图完成')

    male_cleaned_xlsx = cfg.sr_dr / '男胎' / '男胎检测数据_cleaned.xlsx'
    if male_cleaned_xlsx.exists():
        mba = MaleBMIAnalyzer(male_cleaned_xlsx, cfg.kk_dr)
        mba.jikkou_subete()
    else:
        print('【男胎】清洗输出缺失，跳过BMI/生存分析')

    female_cleaned_xlsx = cfg.sr_dr / '女胎' / '女胎检测数据_cleaned.xlsx'
    if female_cleaned_xlsx.exists():
        onna_bunrui_cv(female_cleaned_xlsx, cfg.kk_dr)
    else:
        print('【女胎】清洗输出缺失，跳过分类交叉验证')

    print('\n✅ 全流程完成：')
    for k, v in vars(cfg).items():
        if any(key in k for key in ('dir', 'dr')):
            print(f'   - {k}: {v}')

if __name__ == '__main__':
    shuyou()
