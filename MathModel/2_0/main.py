from pathlib import Path as P
from data_processing import PathConfig, DataCleaner
from analysis import Analyzer
from plotting import Plotter
from bmi_grouping import MaleBMIAnalyzer
from survival_timing import run_survival_timing


def main():
    # --- Adjust paths as needed ---
    cfg = PathConfig(
        src_dir=P('.'),                              # put 附件.xlsx here or change path
        result_dir=P('./Result/AnalysisResult'),
        clean_dir=P('./Result/CleanResult'),
        plot_dir=P('./Result/Plots'),
        log_dir=P('./Result/CleanedLog')
    )

    cleaner = DataCleaner(cfg, filename='附件.xlsx', male_sheet='男胎检测数据', female_sheet='女胎检测数据')
    df_dict = cleaner.run_all(
        zscore_cols=['检测孕周', '孕妇BMI', '年龄', '生产次数'],
        chrom_z_cols=['13号染色体的Z值', '18号染色体的Z值', '21号染色体的Z值', 'X染色体的Z值', 'Y染色体的Z值']
    )
    print('\n✅ 数据清洗完成')

    analyzer = Analyzer(str(cfg.result_dir), str(cfg.log_dir))
    plotter = Plotter(cfg.plot_dir, enable=True)

    for sheet_name, df in df_dict.items():
        gender = '男胎' if '男' in sheet_name else '女胎'
        if gender == '男胎':
            analyzer.correlation_matrix(df, gender, cols=['检测孕周', '孕妇BMI', '年龄', 'Y染色体浓度'])
            analyzer.vif(df, x_cols=['检测孕周', '孕妇BMI', '年龄', '生产次数'], gender=gender)
            analyzer.ols(df, y_col='Y染色体浓度', x_cols=['检测孕周', '孕妇BMI', '年龄', '生产次数'], gender=gender)
            analyzer.mixedlm(df, y_col='Y染色体浓度', x_cols=['检测孕周', '孕妇BMI'], group_col='孕妇代码', gender=gender)
            plotter.y_conc_hist(df, gender)
            plotter.scatter_week_y(df, gender)
            plotter.scatter_bmi_y(df, gender)
        else:
            # 女胎仅做相关/后续分类可在独立脚本扩展
            analyzer.correlation_matrix(df, gender, cols=['X染色体的Z值', '13号染色体的Z值', '18号染色体的Z值', '21号染色体的Z值', '孕妇BMI'])

    print('\n✅ 相关/回归/绘图完成')

    # 男胎 BMI 分组与最早达标孕周
    male_cleaned_path = cfg.clean_dir / '男胎' / '男胎检测数据_cleaned.xlsx'
    if male_cleaned_path.exists():
        bmi_ana = MaleBMIAnalyzer(male_cleaned_path, cfg.result_dir)
        bmi_ana.run_all()
        print('\n✅ 男胎 BMI 分组分析完成')
    else:
        print('\n[警告] 未找到男胎清洗文件，跳过 BMI 分组分析')

    # 生存分析（基于清洗阶段生成的 CSV）
    surv_csv = cfg.clean_dir / '男胎' / 'cleaned_survival_data.csv'
    if surv_csv.exists():
        run_survival_timing(surv_csv, cfg.result_dir / 'survival')
        print('\n✅ 生存分析完成')
    else:
        print('\n[警告] 未找到 cleaned_survival_data.csv，跳过生存分析')

    print('\n✅ 全流程结束，输出目录:')
    for k, v in vars(cfg).items():
        if 'dir' in k:
            print(f"   - {k}: {v}")


if __name__ == '__main__':
    main()
