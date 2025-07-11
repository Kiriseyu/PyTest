from pathlib import Path
from 数据处理 import PathConfig, DataCleaner
from 建模分析 import Analyzer
from 绘图 import Plotter
from BMI分组与检验 import male_bmi_best_week_entry, female_abnormality_entry   # 新增


def main():
    cfg = PathConfig(
        src_dir=Path("C:/Users/26790/Desktop/BoxFilesPic"),
        result_dir=Path("C:/Users/26790/Desktop/Result/AnalysisResult"),
        clean_dir=Path("C:/Users/26790/Desktop/Result/CleanResult"),
        plot_dir=Path("C:/Users/26790/Desktop/Result/Plots"),
        log_dir=Path("C:/Users/26790/Desktop/Result/CleanedLog")
    )

    cleaner = DataCleaner(cfg, filename="附件.xlsx",
                          male_sheet="男胎检测数据",
                          female_sheet="女胎检测数据")
    df_dict = cleaner.run_all(
        zscore_cols=["检测孕周", "孕妇BMI", "年龄", "生产次数"],
        chrom_z_cols=["13号染色体的Z值", "18号染色体的Z值", "21号染色体的Z值",
                      "X染色体的Z值", "Y染色体的Z值"]
    )
    print("\n✅ 数据清洗完成")

    # 男胎回归 & 女胎判定
    analyzer = Analyzer(str(cfg.result_dir), str(cfg.log_dir))
    for sheet_name, df in df_dict.items():
        gender = "男胎" if "男" in sheet_name else "女胎"
        print(f"\n===== 开始分析 {gender} =====")
        if gender == "男胎":
            analyzer.linear_regression(df, "Y染色体浓度",
                                       ["检测孕周", "孕妇BMI", "年龄", "生产次数"], gender)
            analyzer.mixedlm(df, "Y染色体浓度", ["检测孕周", "孕妇BMI"], "孕妇代码", gender)
        else:
            # 女胎只做异常判定
            female_path = str(cfg.clean_dir / "女胎" / "女胎检测数据_cleaned.xlsx")
            female_out = str(cfg.result_dir)          # 与男胎同输出目录
            if Path(female_path).exists():
                print("\n===== 开始女胎异常判定 =====")
                female_abnormality_entry(female_path, female_out)
            else:
                print("\n【女胎】清洗文件不存在，跳过异常判定。")

    # 绘图
    plotter = Plotter(cfg.plot_dir, enable=True)
    for sheet_name, df in df_dict.items():
        gender = "男胎" if "男" in sheet_name else "女胎"
        plotter.histogram(df, "检测孕周", f"{gender}_孕周分布.png", gender)
        plotter.scatter(df, "孕妇BMI", "胎儿游离DNA浓度", f"{gender}_BMI_vs_DNA.png", gender)
        plotter.boxplot(df, "年龄", "胎儿游离DNA浓度", f"{gender}_年龄_vs_DNA.png", gender)

    print("\n✅ 绘图完成，所有结果已保存到:")
    for k, v in vars(cfg).items():
        if 'dir' in k:
            print(f"   - {k}: {v}")

    # 男胎 BMI 最佳时点分析
    male_bmi_best_week_entry(
        cleaned_male_path=str(cfg.clean_dir / '男胎' / '男胎检测数据_cleaned.xlsx'),
        out_dir=str(cfg.result_dir)
    )


if __name__ == "__main__":
    main()