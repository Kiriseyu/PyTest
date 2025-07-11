import re
import os
import glob
from itertools import combinations
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
import networkx as nx

# ---------- 基础设置 ----------
plt.rcParams['font.family'] = 'Microsoft YaHei'
plt.rcParams['axes.unicode_minus'] = False


# ---------- 绘图基类 ----------
class Plotter:
    def __init__(self, df=None, title=None):
        self.df = df
        self.title = title

    def _save_plot(self, name: str):
        """保存图形，自动清理非法字符"""
        # 1. 清理文件名
        safe = re.sub(r'[\\/:*?"<>|()（）]', '_', str(name))
        # 2. 如果目录不存在就创建
        os.makedirs(os.path.dirname(safe) or '.', exist_ok=True)
        # 3. 保存
        plt.tight_layout()
        plt.savefig(f"{safe}.png", dpi=150)
        plt.close()
        print(f"图表 {safe}.png 已保存")

    def show_plot(self):
        plt.show()


# ---------- 具体图表 ----------
# 散点图
class ScatterPlot(Plotter):
    def __init__(self, df, x, y, title=None):
        super().__init__(df, title or f"{x} vs {y}")
        self.x, self.y = x, y

    def plot(self):
        plt.figure()
        sns.scatterplot(data=self.df, x=self.x, y=self.y)
        plt.title(self.title)
        self._save_plot(f"scatter_{self.x}_{self.y}")
        plt.show()

# 折线图
class LinePlot(Plotter):
    def __init__(self, df, x, y, title=None):
        super().__init__(df, title or f"{x}-{y} 折线")
        self.x, self.y = x, y

    def plot(self):
        plt.figure()
        sns.lineplot(data=self.df, x=self.x, y=self.y)
        plt.title(self.title)
        self._save_plot(f"line_{self.x}_{self.y}")
        plt.show()

# 箱线图
class BoxPlot(Plotter):
    def __init__(self, df, columns, title="箱线图"):
        super().__init__(df, title)
        self.columns = columns

    def plot(self):
        plt.figure()
        sns.boxplot(data=self.df[self.columns])
        plt.title(self.title)
        self._save_plot(f"box_{'_'.join(self.columns)}")
        plt.show()

# 热力图
class Heatmap(Plotter):
    def __init__(self, df, columns=None, title="相关性热力图"):
        super().__init__(df, title)
        self.columns = columns or df.select_dtypes(include=[np.number]).columns

    def plot(self):
        plt.figure(figsize=(max(6, len(self.columns)), max(4, len(self.columns))))
        sns.heatmap(self.df[self.columns].corr(), annot=True, cmap="coolwarm", fmt=".2f")
        plt.title(self.title)
        self._save_plot("heatmap")
        plt.show()

# 柱状图
class Histogram(Plotter):
    def __init__(self, df, column, bins=30, title=None):
        super().__init__(df, title or f"{column} 直方图")
        self.column, self.bins = column, bins

    def plot(self):
        plt.figure()
        sns.histplot(self.df[self.column], bins=self.bins, kde=True)
        plt.title(self.title)
        self._save_plot(f"histogram_{self.column}")
        plt.show()

# 成对散点图
class PairPlot(Plotter):
    def __init__(self, df, columns=None, title="成对散点图"):
        super().__init__(df, title)
        self.columns = columns or df.select_dtypes(include=[np.number]).columns

    def plot(self):
        sns.pairplot(self.df[self.columns])
        self._save_plot("pairplot")
        plt.show()

# PCA图
class PCAPlot(Plotter):
    def __init__(self, df, n_components=2, title="PCA"):
        super().__init__(df, title)
        self.n_components = n_components

    def plot(self):
        data = self.df.select_dtypes(include=[np.number])
        pca = PCA(n_components=self.n_components)
        pcs = pca.fit_transform(data)
        pcs = pd.DataFrame(pcs, columns=[f"PC{i+1}" for i in range(self.n_components)])

        plt.figure()
        sns.scatterplot(data=pcs, x="PC1", y="PC2")
        plt.title(self.title)
        plt.xlabel(f"PC1 ({pca.explained_variance_ratio_[0]:.1%})")
        plt.ylabel(f"PC2 ({pca.explained_variance_ratio_[1]:.1%})")
        self._save_plot("pca")
        plt.show()

# t-SNE图
class TSNEPlot(Plotter):
    def __init__(self, df, n_components=2, perplexity=30, title="t-SNE"):
        super().__init__(df, title)
        self.n_components = n_components
        self.perplexity = perplexity

    def plot(self):
        data = self.df.select_dtypes(include=[np.number])
        tsne = TSNE(n_components=self.n_components, perplexity=self.perplexity, random_state=42)
        emb = tsne.fit_transform(data)
        emb = pd.DataFrame(emb, columns=[f"TSNE{i+1}" for i in range(self.n_components)])

        plt.figure()
        sns.scatterplot(data=emb, x="TSNE1", y="TSNE2")
        plt.title(self.title)
        self._save_plot("tsne")
        plt.show()

# 网络图
class NetworkPlot(Plotter):
    def __init__(self, graph=None, title="网络图"):
        super().__init__(title=title)
        self.graph = graph or nx.erdos_renyi_graph(10, 0.5)

    def plot(self):
        plt.figure()
        nx.draw(self.graph, with_labels=True, node_color='skyblue', node_size=500,
                edge_color='gray', width=2, font_size=12)
        plt.title(self.title)
        self._save_plot("network")
        plt.show()


# ---------- 自动发现列并批量调用 ----------
class AutoPlotter:
    """
    根据 DataFrame 自动选择列并绘图
    """
    def __init__(self, df):
        self.df = df
        self.num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        self.cat_cols = [c for c in df.columns if c not in self.num_cols]

    # 下面每个方法都返回“可调用对象”，方便 main() 里开关
    def scatter_all_pairs(self):
        """数值列两两散点图"""
        if len(self.num_cols) < 2:
            return lambda: print("数值列不足 2 列，跳过散点图")
        def _run():
            for x, y in combinations(self.num_cols, 2):
                ScatterPlot(self.df, x, y).plot()
        return _run

    def box_num(self):
        """数值列箱线图"""
        if not self.num_cols:
            return lambda: print("无数值列，跳过箱线图")
        return lambda: BoxPlot(self.df, self.num_cols).plot()

    def heatmap_num(self):
        """数值列热力图"""
        if len(self.num_cols) < 2:
            return lambda: print("数值列不足 2 列，跳过热力图")
        return lambda: Heatmap(self.df).plot()

    def histogram_each(self):
        """每个数值列直方图"""
        if not self.num_cols:
            return lambda: print("无数值列，跳过直方图")
        def _run():
            for col in self.num_cols:
                Histogram(self.df, col).plot()
        return _run

    def pairplot_num(self):
        """成对散点图"""
        if len(self.num_cols) < 2:
            return lambda: print("数值列不足 2 列，跳过 pairplot")
        return lambda: PairPlot(self.df).plot()

    def pca_plot(self):
        """PCA 2D"""
        if len(self.num_cols) < 2:
            return lambda: print("数值列不足 2 列，跳过 PCA")
        return lambda: PCAPlot(self.df).plot()

    def tsne_plot(self):
        """t-SNE 2D"""
        if len(self.num_cols) < 2:
            return lambda: print("数值列不足 2 列，跳过 t-SNE")
        return lambda: TSNEPlot(self.df).plot()

    def network_demo(self):
        """随机网络示例"""
        return lambda: NetworkPlot().plot()


# ---------- main() ----------
def main(folder_path: str,
         do_scatter=True,
         do_box=True,
         do_heatmap=True,
         do_hist=True,
         do_pair=True,
         do_pca=True,
         do_tsne=True,
         do_network=True):
    """
    批量处理一个文件夹里的所有 xlsx，并支持自由开关
    """
    for file in glob.glob(os.path.join(folder_path, "*.xlsx")):
        print(f"\n========== 处理 {os.path.basename(file)} ==========")
        df = pd.read_excel(file)
        ap = AutoPlotter(df)

        # 用 dict 统一调用，避免大量 if
        actions = {
            "scatter": ap.scatter_all_pairs(),
            "box": ap.box_num(),
            "heatmap": ap.heatmap_num(),
            "hist": ap.histogram_each(),
            "pair": ap.pairplot_num(),
            "pca": ap.pca_plot(),
            "tsne": ap.tsne_plot(),
            "network": ap.network_demo(),
        }

        for key, func in actions.items():
            if locals().get(f"do_{key}", False):
                print(f"[运行] {key}")
                func()


if __name__ == "__main__":
    folder = r"C:\Users\26790\Desktop\BoxFilesPic"
    main(folder,
         do_scatter=True,
         do_box=True,
         do_heatmap=True,
         do_hist=True,
         do_pair=True,
         do_pca=True,
         do_tsne=True,
         do_network=True)