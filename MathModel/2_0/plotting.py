from pathlib import Path as _Path
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as _pd

plt.rcParams['axes.unicode_minus'] = False
try:
    plt.rcParams['font.family'] = 'SimHei'
except Exception:
    plt.rcParams['font.sans-serif'] = ['DejaVu Sans']


class Plotter:
    """Minimal, task-focused plots (default PNG)."""
    def __init__(self, base_dir: _Path, enable: bool = True):
        self.base_dir = _Path(base_dir)
        self.enable = enable

    def _save(self, fig, path: _Path):
        if not self.enable:
            plt.close(fig)
            return
        path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(path, dpi=300, bbox_inches='tight')
        plt.close(fig)

    def _gd(self, gender: str):
        d = self.base_dir / gender
        d.mkdir(parents=True, exist_ok=True)
        return d

    def y_conc_hist(self, df: _pd.DataFrame, gender: str):
        if 'Y染色体浓度' not in df.columns: return
        s = _pd.to_numeric(df['Y染色体浓度'], errors='coerce').dropna()
        if s.empty: return
        fig = plt.figure(figsize=(6,4))
        sns.histplot(s, kde=True, bins=30)
        plt.axvline(0.04, color='red', ls='--', label='4% 阈值')
        plt.legend(); plt.title('Y 染色体浓度分布')
        self._save(fig, self._gd(gender)/'Y浓度分布.png')

    def scatter_week_y(self, df: _pd.DataFrame, gender: str):
        if '检测孕周' not in df.columns or 'Y染色体浓度' not in df.columns: return
        x = _pd.to_numeric(df['检测孕周'], errors='coerce')
        y = _pd.to_numeric(df['Y染色体浓度'], errors='coerce')
        m = x.notna() & y.notna()
        if not m.any(): return
        fig = plt.figure(figsize=(6,4))
        plt.scatter(x[m], y[m], s=14)
        plt.axhline(0.04, color='red', ls='--')
        plt.xlabel('孕周'); plt.ylabel('Y浓度'); plt.title('孕周 vs Y浓度')
        self._save(fig, self._gd(gender)/'孕周_vs_Y浓度.png')

    def scatter_bmi_y(self, df: _pd.DataFrame, gender: str):
        if '孕妇BMI' not in df.columns or 'Y染色体浓度' not in df.columns: return
        x = _pd.to_numeric(df['孕妇BMI'], errors='coerce')
        y = _pd.to_numeric(df['Y染色体浓度'], errors='coerce')
        m = x.notna() & y.notna()
        if not m.any(): return
        fig = plt.figure(figsize=(6,4))
        plt.scatter(x[m], y[m], s=14)
        plt.axhline(0.04, color='red', ls='--')
        plt.xlabel('BMI'); plt.ylabel('Y浓度'); plt.title('BMI vs Y浓度')
        self._save(fig, self._gd(gender)/'BMI_vs_Y浓度.png')