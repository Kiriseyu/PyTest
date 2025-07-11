# ------------------ 标准库 ------------------
import os
import re
import json
import warnings
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Dict, Optional, Tuple, Union
from datetime import datetime, date

# ------------------ 第三方库 ------------------
import numpy as np
import pandas as pd
from scipy import stats
from scipy.stats import (
    shapiro, kstest, chi2_contingency,
    pearsonr, spearmanr, kendalltau
)

import matplotlib
matplotlib.use("Agg")                    # 无界面后端
import matplotlib.pyplot as plt
plt.rcParams['font.sans-serif'] = ['Microsoft YaHei']  # 中文
plt.rcParams['axes.unicode_minus'] = False

warnings.filterwarnings("ignore")

# ------------------ 可选依赖 ------------------
try:
    from statsmodels.graphics.gofplots import qqplot
    from statsmodels.tsa.api import SimpleExpSmoothing, ExponentialSmoothing, SARIMAX
    from statsmodels.tsa.stattools import adfuller
except Exception:
    qqplot = SimpleExpSmoothing = ExponentialSmoothing = SARIMAX = adfuller = None

try:
    import tensorflow as tf
    from tensorflow.keras import Sequential
    from tensorflow.keras.layers import LSTM, Dense
except Exception:
    tf = Sequential = LSTM = Dense = None

# =========================================================
# 通用：带日期友好的 JSON 编码器
# =========================================================
class JSONEncoderWithTime(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (datetime, date, pd.Timestamp)):
            return obj.isoformat()
        return super().default(obj)

# =========================================================
# 日志
# =========================================================
@dataclass
class Logger:
    base_dir: Path
    name: str = "pipeline"
    _fp: Optional[Path] = field(default=None, init=False)

    def __post_init__(self):
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self._fp = self.base_dir / f"{self.name}.log"

    def log(self, msg: str):
        line = f"[LOG] {pd.Timestamp.now()} - {msg}"
        print(line)
        with open(self._fp, "a", encoding="utf-8") as f:
            f.write(line + "\n")

    def section(self, title: str):
        self.log("=" * 16 + " " + title + " " + "=" * 16)

    def save_json(self, obj: dict, filename: str):
        p = self.base_dir / filename
        with open(p, "w", encoding="utf-8") as f:
            json.dump(obj, f, ensure_ascii=False, indent=2, cls=JSONEncoderWithTime)
        self.log(f"JSON 结果已保存：{p}")

# =========================================================
# 文件导入
# =========================================================
@dataclass
class FileImporter:
    src_dir: Path
    logger: Logger
    patterns: Tuple[str, ...] = (r".*\.csv$", r".*\.xlsx?$", r".*\.parquet$")

    def list_files(self) -> List[Path]:
        self.logger.section("文件扫描")
        files = []
        for p in self.src_dir.rglob("*"):
            if p.is_file() and any(re.match(pat, p.name, re.I) for pat in self.patterns):
                files.append(p)
        self.logger.log(f"共发现 {len(files)} 个数据文件")
        return files

    def read(self, path: Path) -> pd.DataFrame:
        self.logger.log(f"读取文件：{path}")
        try:
            suffix = path.suffix.lower()
            if suffix == ".csv":
                df = pd.read_csv(path, encoding="utf-8", low_memory=False)
            elif suffix in (".xlsx", ".xls"):
                df = pd.read_excel(path)
            elif suffix == ".parquet":
                df = pd.read_parquet(path)
            else:
                raise ValueError(f"不支持的文件类型：{suffix}")
            self.logger.log(f"数据形状：{df.shape}")
            return df
        except Exception as e:
            self.logger.log(f"读取失败：{e}")
            raise

# =========================================================
# 数据清洗
# =========================================================
@dataclass
class DataCleaner:
    logger: Logger
    clean_dir: Path

    def __post_init__(self):
        self.clean_dir.mkdir(parents=True, exist_ok=True)

    def sanitize_column_names(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.rename(columns=lambda c: re.sub(r'[\\/:*?"<>|()]', '_', str(c)))
        self.logger.log("列名已规范化（非法字符替换为下划线）")
        return df

    def handle_dtype_errors(self, df: pd.DataFrame, numeric_like: Optional[List[str]] = None) -> pd.DataFrame:
        self.logger.section("数据类型纠正")
        numeric_like = numeric_like or []
        for c in numeric_like:
            if c in df.columns:
                bad = df[c].isna().sum()
                df[c] = pd.to_numeric(df[c], errors="coerce")
                now_bad = df[c].isna().sum()
                self.logger.log(f"{c} 转为数值：NaN {bad} -> {now_bad}")
        return df

    def handle_missing(self, df: pd.DataFrame,
                       num_strategy: str = "median",
                       cat_strategy: str = "mode",
                       drop_thresh: Optional[float] = None) -> pd.DataFrame:
        self.logger.section("缺失值处理")
        miss_report = df.isna().mean().sort_values(ascending=False).to_dict()
        self.logger.save_json({"missing_ratio": miss_report}, "missing_report.json")

        if drop_thresh is not None:
            to_drop = [c for c, r in miss_report.items() if r >= drop_thresh]
            if to_drop:
                self.logger.log(f"删除缺失比例≥{drop_thresh}的列：{to_drop}")
                df = df.drop(columns=to_drop)

        numeric_cols = df.select_dtypes(include=[np.number]).columns
        cat_cols = [c for c in df.columns if c not in numeric_cols]

        for c in numeric_cols:
            if df[c].isna().any():
                fill = df[c].median() if num_strategy == "median" else (df[c].mean() if num_strategy == "mean" else 0)
                df[c] = df[c].fillna(fill)
                self.logger.log(f"[数值列] {c} 缺失填充为 {fill}")

        for c in cat_cols:
            if df[c].isna().any():
                fill = df[c].mode(dropna=True).iloc[0] if cat_strategy == "mode" and not df[c].mode(dropna=True).empty else "missing"
                df[c] = df[c].fillna(fill)
                self.logger.log(f"[类别列] {c} 缺失填充为 {fill}")
        return df

    def handle_outliers(self, df: pd.DataFrame, method: str = "iqr", factor: float = 1.5) -> pd.DataFrame:
        self.logger.section("异常值处理")
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        changed = {}
        for c in numeric_cols:
            series = df[c].astype(float)
            if method == "zscore":
                z = np.abs(stats.zscore(series, nan_policy="omit"))
                mask = z > 3
                capped = series.clip(lower=series.quantile(0.01), upper=series.quantile(0.99))
                df.loc[mask, c] = capped[mask]
                changed[c] = int(mask.sum())
            else:  # IQR
                q1, q3 = np.nanpercentile(series, [25, 75])
                iqr = q3 - q1
                lb, ub = q1 - factor * iqr, q3 + factor * iqr
                mask = (series < lb) | (series > ub)
                df.loc[mask, c] = series.clip(lb, ub)
                changed[c] = int(mask.sum())
        self.logger.save_json({"outliers_capped": changed, "method": method}, "outliers_report.json")
        return df

    def handle_format_logic(self, df: pd.DataFrame,
                            date_cols: Optional[List[str]] = None,
                            non_negative_cols: Optional[List[str]] = None) -> pd.DataFrame:
        self.logger.section("格式/逻辑处理")
        date_cols = date_cols or []
        non_negative_cols = non_negative_cols or []

        for c in date_cols:
            if c in df.columns:
                before_na = df[c].isna().sum()
                df[c] = pd.to_datetime(df[c], errors="coerce")
                after_na = df[c].isna().sum()
                self.logger.log(f"日期列 {c} 解析：NaN {before_na} -> {after_na}")

        for c in non_negative_cols:
            if c in df.columns:
                neg_count = (df[c] < 0).sum()
                df.loc[df[c] < 0, c] = 0
                self.logger.log(f"非负列 {c} 负值纠正数量：{int(neg_count)}")
        return df

    def handle_duplicates(self, df: pd.DataFrame, subset: Optional[List[str]] = None) -> pd.DataFrame:
        self.logger.section("重复值处理")
        before = len(df)
        df = df.drop_duplicates(subset=subset)
        self.logger.log(f"去重：{before} -> {len(df)}，删除 {before - len(df)} 行")
        return df

    def handle_redundancy(self, df: pd.DataFrame, corr_thresh: float = 0.98) -> pd.DataFrame:
        self.logger.section("冗余信息处理")
        dropped = []

        const_cols = df.columns[df.nunique(dropna=False) <= 1].tolist()
        if const_cols:
            df = df.drop(columns=const_cols)
            dropped += const_cols
            self.logger.log(f"删除常量列：{const_cols}")

        num = df.select_dtypes(include=[np.number])
        if num.shape[1] >= 2:
            corr = num.corr().abs()
            upper = corr.where(np.triu(np.ones(corr.shape), k=1).astype(bool))
            to_drop = [col for col in upper.columns if any(upper[col] > corr_thresh)]
            if to_drop:
                df = df.drop(columns=to_drop)
                dropped += to_drop
                self.logger.log(f"删除高相关列(>|{corr_thresh}|)：{to_drop}")

        self.logger.save_json({"dropped_columns": dropped}, "redundancy_report.json")
        return df

# =========================================================
# 数据分析
# =========================================================
@dataclass
class DataAnalyzer:
    logger: Logger
    result_dir: Path

    def __post_init__(self):
        self.result_dir.mkdir(parents=True, exist_ok=True)

    def descriptive_stats(self, df: pd.DataFrame) -> Dict:
        self.logger.section("数据初筛与特征识别")
        desc = {
            "集中趋势": {},
            "离散程度": {},
            "分布形态": {},
            "分组统计示例": {}
        }
        num = df.select_dtypes(include=[np.number])

        for c in num.columns:
            series = num[c].dropna()
            desc["集中趋势"][c] = {
                "均值": float(series.mean()),
                "中位数": float(series.median()),
                "众数": float(series.mode().iloc[0]) if not series.mode().empty else None
            }
            desc["离散程度"][c] = {
                "标准差": float(series.std()),
                "方差": float(series.var()),
                "四分位距": float(series.quantile(0.75) - series.quantile(0.25))
            }
            desc["分布形态"][c] = {
                "偏度": float(series.skew()),
                "峰度": float(series.kurt())
            }

        cat_cols = [c for c in df.columns if c not in num.columns]
        if cat_cols:
            gcol = cat_cols[0]
            desc["分组统计示例"][gcol] = {
                "分组计数": df[gcol].value_counts(dropna=False).rename(index=str).to_dict()
            }
            for c in num.columns[:3]:
                desc["分组统计示例"][f"{gcol} - {c}均值"] = (
                    df.groupby(gcol)[c]
                    .mean()
                    .dropna()
                    .rename(index=str)
                    .to_dict()
                )
        self.logger.save_json(desc, "descriptive_stats.json")
        return desc

    def distribution_tests(self, df: pd.DataFrame) -> Dict:
        self.logger.section("分布检验")
        num = df.select_dtypes(include=[np.number])
        res = {"Shapiro-Wilk": {}, "Kolmogorov-Smirnov": {}}
        for c in num.columns:
            series = num[c].dropna()
            if len(series) < 3:
                continue
            if len(series) < 50:
                stat, p = shapiro(series)
                res["Shapiro-Wilk"][c] = {"stat": float(stat), "p": float(p)}
            else:
                m, s = series.mean(), series.std(ddof=0)
                if s == 0 or np.isnan(s):
                    continue
                z = (series - m) / s
                stat, p = kstest(z, "norm")
                res["Kolmogorov-Smirnov"][c] = {"stat": float(stat), "p": float(p)}
        self.logger.save_json(res, "distribution_tests.json")
        return res

    def correlation_analysis(self, df: pd.DataFrame) -> Dict:
        self.logger.section("关联性分析")
        result = {"Pearson": {}, "Spearman": {}, "Kendall": {}, "ChiSquare": {}}
        num = df.select_dtypes(include=[np.number]).columns.tolist()

        # 数值-数值
        for i in range(len(num)):
            for j in range(i + 1, len(num)):
                a, b = num[i], num[j]
                s1, s2 = df[a].astype(float), df[b].astype(float)
                try:
                    r, p = pearsonr(s1, s2)
                    result["Pearson"][f"{a}-{b}"] = {"r": float(r), "p": float(p)}
                except Exception:
                    pass
                try:
                    r, p = spearmanr(s1, s2)
                    result["Spearman"][f"{a}-{b}"] = {"r": float(r), "p": float(p)}
                except Exception:
                    pass
                try:
                    r, p = kendalltau(s1, s2)
                    result["Kendall"][f"{a}-{b}"] = {"r": float(r), "p": float(p)}
                except Exception:
                    pass

        # 类别-类别
        cat = [c for c in df.columns if c not in num]
        for i in range(len(cat)):
            for j in range(i + 1, len(cat)):
                a, b = cat[i], cat[j]
                try:
                    table = pd.crosstab(df[a], df[b])
                    chi2, p, dof, exp = chi2_contingency(table)
                    result["ChiSquare"][f"{a}-{b}"] = {"chi2": float(chi2), "p": float(p), "dof": int(dof)}
                except Exception:
                    pass
        self.logger.save_json(result, "correlation_analysis.json")
        return result

    def forecast(self, series: pd.Series,
                 method: str = "ma",
                 ma_window: int = 3,
                 es_trend: Optional[str] = None,
                 order: Tuple[int, int, int] = (1, 1, 1),
                 seasonal_order: Tuple[int, int, int, int] = (0, 0, 0, 0),
                 steps: int = 12) -> Dict:
        self.logger.section(f"预测 - {method.upper()}")
        s = series.dropna().astype(float)
        if s.empty:
            self.logger.log("空序列，跳过预测")
            return {}

        if method == "ma":
            pred = s.rolling(window=ma_window, min_periods=1).mean().iloc[-1]
            res = {"method": "MA", "last_ma": float(pred), "forecast": [float(pred)] * steps}



        elif method == "es":

            if SimpleExpSmoothing is None:
                self.logger.log("缺少 statsmodels，无法使用 ES")

                return {}

            try:

                model = SimpleExpSmoothing(s).fit()

                fc = model.forecast(steps)

                res = {"method": "ES", "forecast": [float(x) for x in fc]}

            except Exception as e:

                self.logger.log(f"ES 拟合失败：{e}，改用 MA")

                pred = s.rolling(window=3, min_periods=1).mean().iloc[-1]

                res = {"method": "MA(fallback)", "last_ma": float(pred), "forecast": [float(pred)] * steps}


        elif method in ("arima", "sarima"):
            if SARIMAX is None:
                self.logger.log("缺少 statsmodels，无法使用 ARIMA/SARIMA")
                return {}
            if method == "arima":
                seasonal_order = (0, 0, 0, 0)

            try:
                model = SARIMAX(s, order=order, seasonal_order=seasonal_order,
                                enforce_stationarity=False, enforce_invertibility=False)
                fit = model.fit(disp=False, maxiter=1000)
            except Exception as e:
                self.logger.log(f"SARIMAX 原始配置收敛失败：{e}，尝试简化模型")
                # 降级：ARIMA(0,1,1)
                try:
                    model = SARIMAX(s, order=(0, 1, 1), seasonal_order=(0, 0, 0, 0),
                                    enforce_stationarity=False, enforce_invertibility=False)
                    fit = model.fit(disp=False, maxiter=1000)
                except Exception as e2:
                    self.logger.log(f"SARIMAX 简化模型仍失败：{e2}，跳过预测")
                    return {}

            fc = fit.forecast(steps)
            res = {
                "method": method.upper(),
                "order": order,
                "seasonal_order": seasonal_order,
                "forecast": [float(x) for x in fc]
            }

        elif method == "lstm":
            if tf is None or Sequential is None:
                self.logger.log("未安装 TensorFlow，跳过 LSTM")
                return {}
            values = s.values.astype("float32")
            lag = 3
            X, y = [], []
            for i in range(len(values) - lag):
                X.append(values[i:i + lag])
                y.append(values[i + lag])
            X = np.array(X).reshape(-1, lag, 1)
            y = np.array(y)

            model = Sequential([LSTM(32, input_shape=(lag, 1)), Dense(1)])
            model.compile(optimizer="adam", loss="mse")
            model.fit(X, y, epochs=10, batch_size=8, verbose=0)

            last = values[-lag:].reshape(1, lag, 1)
            preds = []
            cur = last.copy()
            for _ in range(steps):
                nxt = model.predict(cur, verbose=0)[0, 0]
                preds.append(float(nxt))
                cur = np.concatenate([cur[:, 1:, :], [[[nxt]]]], axis=1)
            res = {"method": "LSTM", "forecast": preds}
        else:
            self.logger.log(f"未知方法：{method}")
            return {}
        self.logger.save_json(res, f"forecast_{method}.json")
        return res

# =========================================================
# 可视化
# =========================================================
@dataclass
class Visualizer:
    logger: Logger
    fig_dir: Path

    def __post_init__(self):
        self.fig_dir.mkdir(parents=True, exist_ok=True)

    def _save_fig(self, name: str):
        p = self.fig_dir / f"{name}.png"
        plt.tight_layout()
        plt.savefig(p, dpi=150)
        plt.close()
        self.logger.log(f"图表已保存：{p}")

    def bar(self, series: pd.Series, title: str = "柱状图"):
        plt.figure()
        series.plot(kind="bar")
        plt.title(title)
        self._save_fig(f"bar_{series.name or 'series'}")

    def pie(self, series: pd.Series, title: str = "饼图"):
        plt.figure()
        series.plot(kind="pie", autopct="%.1f%%")
        plt.ylabel("")
        plt.title(title)
        self._save_fig(f"pie_{series.name or 'series'}")

    def box(self, df: pd.DataFrame, cols: Optional[List[str]] = None, title: str = "箱线图"):
        plt.figure()
        (df[cols] if cols else df.select_dtypes(include=[np.number])).plot(kind="box")
        plt.title(title)
        self._save_fig("boxplot")

    def scatter(self, df: pd.DataFrame, x: str, y: str, title: str = "散点图"):
        plt.figure()
        plt.scatter(df[x], df[y])
        plt.xlabel(x)
        plt.ylabel(y)
        plt.title(title)
        self._save_fig(f"scatter_{x}_{y}")

    def heatmap(self, df: pd.DataFrame, title: str = "热力图(相关系数)"):
        # 先筛选出数值型列
        num = df.select_dtypes(include=[np.number])

        # 去掉常量列（方差为 0）
        num = num.loc[:, num.var() > 0]

        # 计算相关系数矩阵并填充 NaN 为 0
        corr = num.corr().fillna(0)

        # 绘制热力图
        plt.figure()
        plt.imshow(corr, interpolation="nearest")
        plt.colorbar()
        plt.xticks(range(len(corr.columns)), corr.columns, rotation=90)
        plt.yticks(range(len(corr.columns)), corr.columns)
        plt.title(title)

        # 保存图表
        self._save_fig("heatmap_corr")

    def qq(self, series: pd.Series, title: str = "Q-Q 图"):
        if qqplot is None:
            self.logger.log("缺少 statsmodels，无法绘制 Q-Q 图")
            return
        plt.figure()
        qqplot(series.dropna(), line="s")
        plt.title(title)
        self._save_fig(f"qq_{series.name or 'series'}")

# =========================================================
# 主流程
# =========================================================
@dataclass
class Pipeline:
    log_path: Path = Path(r"C:\Users\26790\Desktop\CleanedLog")
    clean_out_path: Path = Path(r"C:\Users\26790\Desktop\Result\AnalysisResult")
    analysis_out_path: Path = Path(r"C:\Users\26790\Desktop\Result\CleanResult")
    figure_out_path: Path = Path(r"C:\Users\26790\Desktop\Result\Plotting")
    src_dir: Path = Path(r"C:\Users\26790\Desktop\BoxFilesPic")
    save_format: str = "xlsx"

    def __post_init__(self):
        self.logger = Logger(self.log_path, name="clean_analyze")
        self.cleaner = DataCleaner(self.logger, self.clean_out_path)
        self.analyzer = DataAnalyzer(self.logger, self.analysis_out_path)
        self.viz = Visualizer(self.logger, self.figure_out_path)
        self.importer = FileImporter(self.src_dir, self.logger)

    def save_processed_file(self, df: pd.DataFrame, original_file: Path):
        file_name = f"{original_file.stem}_processed.{self.save_format}"
        save_path = self.clean_out_path / file_name
        if self.save_format == "csv":
            df.to_csv(save_path, index=False, encoding="utf-8")
        elif self.save_format == "xlsx":
            df.to_excel(save_path, index=False)
        elif self.save_format == "parquet":
            df.to_parquet(save_path, index=False)
        else:
            self.logger.log(f"不支持的文件格式：{self.save_format}")
            return
        self.logger.log(f"处理后的文件已保存：{save_path}")
        return save_path

    def run(self):
        self.logger.section("主运行开始")
        files = self.importer.list_files()
        if not files:
            self.logger.log("未发现可处理的数据文件，流程结束。")
            return

        for fp in files:
            self.logger.section(f"处理文件：{fp.name}")
            try:
                df = self.importer.read(fp)
                df = self.cleaner.sanitize_column_names(df)

                # --- 类型转换之前，先筛掉编码列 ---
                exclude_cols = [c for c in df.columns if re.search(r"(id|code|编号|编码)", c, re.I)]
                numeric_like = [c for c in df.columns
                                if c not in exclude_cols
                                and re.search(r"(amt|price|qty|num|count|rate)", c, re.I)]

                # 调用 handle_dtype_errors 执行数值列转换
                df = self.cleaner.handle_dtype_errors(df, numeric_like)

                # 清洗
                df = self.cleaner.handle_missing(df, num_strategy="median", cat_strategy="mode", drop_thresh=0.9)
                df = self.cleaner.handle_outliers(df, method="iqr", factor=1.5)
                date_guess = [c for c in df.columns if re.search(r"(date|time|dt|day|month|year)", c, re.I)]
                df = self.cleaner.handle_format_logic(df, date_cols=date_guess, non_negative_cols=[])
                df = self.cleaner.handle_duplicates(df)
                df = self.cleaner.handle_redundancy(df)

                self.save_processed_file(df, fp)

                # 分析
                desc = self.analyzer.descriptive_stats(df)
                dist = self.analyzer.distribution_tests(df)
                corr = self.analyzer.correlation_analysis(df)

                num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
                if num_cols:
                    s = df[num_cols[0]]
                    self.analyzer.forecast(s, method="ma", ma_window=3, steps=12)
                    if SimpleExpSmoothing is not None:
                        self.analyzer.forecast(s, method="es", steps=12)
                    if SARIMAX is not None:
                        self.analyzer.forecast(s, method="arima", order=(1, 1, 1), steps=12)

                # 可视化
                cat_cols = [c for c in df.columns if c not in num_cols]
                if cat_cols:
                    vc = df[cat_cols[0]].value_counts().head(10)
                    self.viz.bar(vc, title=f"Top类别计数 - {cat_cols[0]}")
                    self.viz.pie(vc, title=f"Top类别占比 - {cat_cols[0]}")
                if num_cols:
                    self.viz.box(df[num_cols], title="数值列箱线图")
                    if len(num_cols) >= 2:
                        self.viz.scatter(df, num_cols[0], num_cols[1], title=f"散点图 {num_cols[0]} vs {num_cols[1]}")
                    self.viz.heatmap(df, title="相关系数热力图")
                    if qqplot is not None:
                        self.viz.qq(df[num_cols[0]], title=f"Q-Q 图 - {num_cols[0]}")

                summary = {
                    "file": str(fp),
                    "shape": df.shape,
                    "desc_keys": list(desc.keys()),
                    "dist_keys": list(dist.keys()),
                    "corr_counts": {k: len(v) for k, v in corr.items()},
                }
                self.logger.save_json(summary, f"summary_{fp.stem}.json")
            except Exception as e:
                self.logger.log(f"处理失败：{fp.name}，原因：{e}")

        self.logger.section("主运行结束")


# =========================================================
# 入口
# =========================================================
if __name__ == "__main__":
    pipeline = Pipeline()
    pipeline.run()
