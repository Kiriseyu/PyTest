import warnings
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats

warnings.filterwarnings("ignore")


@dataclass
class PlotConfig:
    enable: bool
    base_dir: Path

    def gender_dir(self, gender: str) -> Path:
        d = self.base_dir / gender
        d.mkdir(parents=True, exist_ok=True)
        return d


def setup_chinese():
    plt.rcParams['axes.unicode_minus'] = False
    try:
        plt.rcParams['font.family'] = 'SimHei'
    except Exception:
        plt.rcParams['font.sans-serif'] = ['DejaVu Sans']


class Plotter:
    """与 main.py 的调用保持一致：构造传 Path，提供 histogram / scatter / boxplot。"""
    def __init__(self, base_dir: Path, enable: bool = True):
        self.cfg = PlotConfig(enable=enable, base_dir=base_dir)
        setup_chinese()

    def _maybe_save(self, fig, path: Path):
        if not self.cfg.enable:
            plt.close(fig)
            return
        path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(path, dpi=300, bbox_inches='tight')
        plt.close(fig)

    def histogram(self, df: pd.DataFrame, col: str, out_name: str, gender: Optional[str] = None):
        if col not in df.columns:
            return
        series = pd.to_numeric(df[col], errors="coerce").dropna()
        if series.empty:
            return
        fig = plt.figure(figsize=(6, 4))
        sns.histplot(series, kde=True)
        plt.title(f"{col} 直方图")
        out = self.cfg.gender_dir(gender or "通用") / out_name
        self._maybe_save(fig, out)

    def scatter(self, df: pd.DataFrame, x: str, y: str, out_name: str, gender: Optional[str] = None):
        if x not in df.columns or y not in df.columns:
            return
        xs = pd.to_numeric(df[x], errors="coerce")
        ys = pd.to_numeric(df[y], errors="coerce")
        mask = xs.notna() & ys.notna()
        if not mask.any():
            return
        fig = plt.figure(figsize=(6, 4))
        plt.scatter(xs[mask], ys[mask], s=14)
        plt.xlabel(x); plt.ylabel(y); plt.title(f"{x} vs {y}")
        out = self.cfg.gender_dir(gender or "通用") / out_name
        self._maybe_save(fig, out)

    def boxplot(self, df: pd.DataFrame, x: str, y: str, out_name: str, gender: Optional[str] = None):
        if x not in df.columns or y not in df.columns:
            return
        tmp = df[[x, y]].copy()
        tmp[y] = pd.to_numeric(tmp[y], errors="coerce")
        tmp = tmp.dropna()
        if tmp.empty:
            return
        fig = plt.figure(figsize=(6, 4))
        sns.boxplot(data=tmp, x=x, y=y)
        plt.title(f"{x} 对 {y} 的箱线图")
        out = self.cfg.gender_dir(gender or "通用") / out_name
        self._maybe_save(fig, out)
