# --------------------------------------------------
# 0. 导包
# --------------------------------------------------
import sys
import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.preprocessing import (
    OneHotEncoder, StandardScaler, MinMaxScaler,
    RobustScaler, PowerTransformer, KBinsDiscretizer
)
from sklearn.feature_selection import SelectKBest, f_classif
from sklearn.decomposition import PCA
import logging

# --------------------------------------------------
# 1. 路径导入 & 日志
# --------------------------------------------------
BASE_DIR = Path(r"C:\Users\26790\Desktop\BoxFilesPic")
OUT_DIR  = Path(r"C:\Users\26790\Desktop\数据清洗")
LOG_DIR  = Path(r"C:\Users\26790\Desktop\CleanedLog")
LOG_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s: %(message)s",
    handlers=[
        logging.FileHandler(LOG_DIR / "run.log", encoding="utf-8"),
        logging.StreamHandler(sys.stdout)
    ]
)
log = logging.getLogger("VegPipeline")

# --------------------------------------------------
# 2. 读取并规范化小表
# --------------------------------------------------
def load_raw():
    log.info("开始读取原始数据...")

    # 1) 单品-分类映射
    prod = pd.read_excel(BASE_DIR / "附件1.xlsx", sheet_name=0)
    prod.columns = prod.columns.str.strip()

    # 2) 批发价格
    price = pd.read_excel(BASE_DIR / "附件3.xlsx", sheet_name=0)
    price.columns = price.columns.str.strip()

    # 3) 损耗率 —— 注意：附件4 第二张表才是单品级
    loss = pd.read_excel(BASE_DIR / "附件4.xlsx", sheet_name=1)  # 关键：读第二张
    loss.columns = loss.columns.str.strip()

    # 打印一下，确认列名
    log.debug("loss.columns = %s", loss.columns.tolist())

    # 如列名仍不匹配，可以手动重命名
    loss = loss.rename(columns={
        "单品编码": "单品编码",
        "损耗率(%)": "损耗率"
    })

    # 合并
    df = price.merge(prod[["单品编码", "分类名称"]], on="单品编码", how="left")
    df = df.merge(loss[["单品编码", "损耗率"]], on="单品编码", how="left")

    log.info("合并后 shape=%s", df.shape)
    return df
# --------------------------------------------------
# 2. DataCleaning
# --------------------------------------------------
class DataCleaning:
    @staticmethod
    def drop_missing(df, threshold=0.4):
        """缺失率>threshold的列直接删除"""
        missing_ratio = df.isnull().mean()
        drop_cols = missing_ratio[missing_ratio > threshold].index.tolist()
        df = df.drop(columns=drop_cols)
        log.info(f"缺失列删除: {drop_cols}")
        return df

    @staticmethod
    def fix_outliers(df, col, low_q=0.01, high_q=0.99):
        """用上下1%分位数截断异常值"""
        low, high = df[col].quantile([low_q, high_q])
        df[col] = df[col].clip(lower=low, upper=high)
        log.info(f"{col} 异常值截断: [{low:.2f}, {high:.2f}]")
        return df

    @staticmethod
    def dedup(df, subset):
        """按给定列去重"""
        before = len(df)
        df = df.drop_duplicates(subset=subset)
        log.info(f"去重: {before} -> {len(df)}")
        return df

# --------------------------------------------------
# 3. DataTransfomation
# --------------------------------------------------
class DataTransfomation:
    @staticmethod
    def type_cast(df):
        df["日期"] = pd.to_datetime(df["日期"])
        df["批发价格(元/千克)"] = pd.to_numeric(df["批发价格(元/千克)"], errors="coerce")
        log.info("类型转换完成")
        return df

    @staticmethod
    def encode_categories(df, cat_col="分类名称"):
        encoder = OneHotEncoder(sparse=False, handle_unknown="ignore")
        encoded = encoder.fit_transform(df[[cat_col]])
        encoded_df = pd.DataFrame(encoded, columns=encoder.get_feature_names_out([cat_col]))
        df = pd.concat([df.reset_index(drop=True), encoded_df.reset_index(drop=True)], axis=1)
        log.info("One-Hot 编码完成")
        return df, encoder

    @staticmethod
    def date_features(df):
        df["weekday"] = df["日期"].dt.weekday
        df["month"]   = df["日期"].dt.month
        log.info("日期特征生成完成")
        return df

    @staticmethod
    def discretize_price(df, n_bins=5):
        dis = KBinsDiscretizer(n_bins=n_bins, encode="ordinal", strategy="quantile")
        df["price_bin"] = dis.fit_transform(df[["批发价格(元/千克)"]]).astype(int)
        log.info(f"批发价格离散化为 {n_bins} 个桶")
        return df, dis

# --------------------------------------------------
# Scaling
# --------------------------------------------------
class Scalers:
    METHODS = {
        "minmax": MinMaxScaler,
        "zscore": StandardScaler,
        "robust": RobustScaler,
        "power":  PowerTransformer
    }

    @staticmethod
    def scale(df, cols, method="zscore"):
        scaler = Scalers.METHODS[method]()
        df[cols] = scaler.fit_transform(df[cols])
        log.info(f"{method} 归一化完成")
        return df, scaler

# --------------------------------------------------
# Dimensionality Reduction
# --------------------------------------------------
class DimReducer:
    @staticmethod
    def select_k_best(X, y, k=10):
        sel = SelectKBest(f_classif, k=k)
        X_new = sel.fit_transform(X, y)
        selected = np.array(X.columns)[sel.get_support()]
        log.info(f"特征选择: {list(selected)}")
        return pd.DataFrame(X_new, columns=selected), sel

    @staticmethod
    def pca(X, n_components=0.95):
        pca = PCA(n_components=n_components, random_state=42)
        X_pca = pca.fit_transform(X)
        log.info(f"PCA 降维: {X.shape[1]} -> {X_pca.shape[1]}")
        return pd.DataFrame(X_pca), pca

# --------------------------------------------------
# 主流程
# --------------------------------------------------
def main():
    log.info("=== 阶段化数据清洗脚本启动 ===")
    df = load_raw()

    # 2. 清洗
    df = DataCleaning.drop_missing(df)
    df = DataCleaning.fix_outliers(df, "批发价格(元/千克)")
    df = DataCleaning.dedup(df, subset=["日期", "单品编码"])

    # 3. 转换
    df = DataTransfomation.type_cast(df)
    df = DataTransfomation.date_features(df)
    df, _ = DataTransfomation.encode_categories(df)
    df, _ = DataTransfomation.discretize_price(df)

    # 4. 归一化（数值列）
    num_cols = ["批发价格(元/千克)", "损耗率(%)"]
    df, _ = Scalers.scale(df, num_cols, method="robust")

    # 5. 降维示例（假设有标签 y）
    feature_cols = [c for c in df.columns if c.startswith("cat_") or c in ["weekday", "month", "price_bin"]]
    X = df[feature_cols]
    y = np.random.randint(0, 2, size=len(df))  # 占位标签
    X_sel, _ = DimReducer.select_k_best(X, y, k=8)
    X_pca, _ = DimReducer.pca(X_sel, n_components=0.9)

    # 保存
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    df.to_parquet(OUT_DIR / "cleaned.parquet")
    X_pca.to_parquet(OUT_DIR / "reduced.parquet")
    log.info("=== 所有阶段完成，结果已保存 ===")

if __name__ == "__main__":
    main()