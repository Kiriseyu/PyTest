import os
import sys
import logging
import pandas as pd
import numpy as np
# from datetime import datetime

# ==================== 配置参数 ====================
INPUT_FILE = "工作簿1.xlsx"
SHEET_NAME = "Sheet1"
OUTPUT_DIR = "result"
os.makedirs(OUTPUT_DIR, exist_ok=True)

OUTPUT_FILE = os.path.join(OUTPUT_DIR, "cleaned_with_clr.xlsx")
LOG_FILE = os.path.join(OUTPUT_DIR, "data_processing.log")

CHEM_COLS = [
    "二氧化硅(SiO2)", "氧化钠(Na2O)", "氧化钾(K2O)", "氧化钙(CaO)",
    "氧化镁(MgO)", "氧化铝(Al2O3)", "氧化铁(Fe2O3)", "氧化铜(CuO)",
    "氧化铅(PbO)", "氧化钡(BaO)", "五氧化二磷(P2O5)",
    "氧化锶(SrO)", "氧化锡(SnO2)", "二氧化硫(SO2)"
]

# ==================== 日志配置 ====================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE, encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


# ==================== 核心处理函数 ====================
def process_data():
    try:
        # 读取原始数据
        logger.info(f"开始读取文件: {INPUT_FILE}")
        df = pd.read_excel(INPUT_FILE, sheet_name=SHEET_NAME)
        logger.info(f"原始数据加载完成，共 {len(df)} 行")

        # 解析文物编号和采样部位
        logger.info("解析文物采样点...")

        def parse_sample_point(s):
            s = str(s).strip()
            num = ''.join(filter(str.isdigit, s)) or "0"
            part = s.replace(num, '', 1).strip('_')
            return pd.Series([num, part or "未知部位"])

        df[["文物编号", "采样部位"]] = df["文物采样点"].apply(parse_sample_point)

        # 处理化学成分数据
        logger.info("处理化学成分数据...")
        mass_cols = [f"质量分数_{col}" for col in CHEM_COLS]

        # 转换数据类型并处理缺失值
        for src_col, tgt_col in zip(CHEM_COLS, mass_cols):
            df[tgt_col] = pd.to_numeric(df[src_col], errors="coerce").fillna(0)

        # 计算成分总和并验证有效性
        df["成分总和"] = df[mass_cols].sum(axis=1)
        valid_mask = df["成分总和"].between(85.0, 105.0, inclusive="both")
        invalid_count = (~valid_mask).sum()

        logger.info(f"发现 {invalid_count} 条无效数据（成分总和不在85-105%之间）")
        df_clean = df[valid_mask].copy()

        # 中心对数变换 (CLR)
        logger.info("执行中心对数变换...")
        chem_data = df_clean[mass_cols].values.astype(np.float64)

        # 数值稳定性处理
        chem_data = np.clip(chem_data, 1e-9, None)  # 限制最小值
        log_data = np.log(chem_data)

        # 计算几何均值（排除全零行）
        with np.errstate(invalid='ignore'):
            geometric_mean = np.exp(log_data.mean(axis=1))

        # 执行CLR变换
        clr_data = log_data - np.log(geometric_mean)[:, np.newaxis]

        # 创建结果DataFrame
        df_result = df_clean.copy()
        for i, col in enumerate(CHEM_COLS):
            df_result[f"CLR_{col}"] = clr_data[:, i]

        # 保存最终结果
        logger.info("保存处理结果...")
        output_cols = ['文物编号', '采样部位', '类型', '表面风化'] + mass_cols + [f"CLR_{c}" for c in CHEM_COLS]
        df_result[output_cols].to_excel(OUTPUT_FILE, index=False)

        logger.info(f"处理完成！结果已保存至: {os.path.abspath(OUTPUT_FILE)}")
        logger.info("=" * 50 + "\n")

    except FileNotFoundError:
        logger.error(f"错误：输入文件 {INPUT_FILE} 不存在")
        sys.exit(1)
    except Exception as e:
        logger.error(f"处理过程中发生意外错误: {str(e)}", exc_info=True)
        sys.exit(1)


# ==================== 主程序入口 ====================
if __name__ == "__main__":
    process_data()