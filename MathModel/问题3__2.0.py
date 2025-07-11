"""
glass_classification_optimized.py
功能：对玻璃文物化学成分做类型预测，并进行全面敏感性分析。
作者：Your Name
日期：2025-08-24
"""

# import os
import time
import warnings
import logging
from pathlib import Path

import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import (
    GridSearchCV, KFold, train_test_split, cross_val_score
)
from sklearn.metrics import (
    classification_report, accuracy_score, roc_curve, auc
)
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline

warnings.filterwarnings("ignore")

# ------------------ 全局配置 ------------------
RANDOM_STATE = 42
DATA_DIR = Path(r"./InputFiles")
IMG_DIR = Path("./output_images")
IMG_DIR.mkdir(exist_ok=True)

sns.set_style("whitegrid")
plt.rcParams["font.family"] = ["SimHei","Microsoft YaHei"]
plt.rcParams["axes.unicode_minus"] = False

logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(message)s",
    level=logging.INFO,
    datefmt="%H:%M:%S"
)

# ------------------ 1. 读取数据 ------------------
known_path = DATA_DIR / "问题三—表单2.xlsx"
unknown_path = DATA_DIR / "问题三—表单3.xlsx"

known_df = pd.read_excel(known_path)
unknown_df = pd.read_excel(unknown_path)

logging.info(f"已知类别数据形状：{known_df.shape}")
logging.info(f"未知类别数据形状：{unknown_df.shape}")

# ------------------ 2. 数据准备 ------------------
X = known_df.drop(columns=["文物编号", "类型", "表面风化"])
y = known_df["类型"]

X_unlabeled = unknown_df.drop(columns=["文物编号"])

# ------------------ 3. 训练 / 调优模型 ------------------
pipe = Pipeline(
    steps=[
        ("scaler", StandardScaler()),
        ("clf", RandomForestClassifier(
            random_state=RANDOM_STATE,
            class_weight="balanced"
        ))
    ]
)

param_grid = {
    "clf__n_estimators": [100, 300, 500],
    "clf__max_depth": [None, 5, 10],
    "clf__min_samples_split": [2, 5]
}

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=RANDOM_STATE, stratify=y
)

gs = GridSearchCV(
    pipe,
    param_grid,
    cv=KFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE),
    scoring="accuracy",
    n_jobs=-1,
    verbose=0
)
gs.fit(X_train, y_train)

best_model = gs.best_estimator_
logging.info(f"最佳参数：{gs.best_params_}")
logging.info(f"交叉验证最优准确率：{gs.best_score_:.4f}")

# 在测试集上评估
y_pred = best_model.predict(X_test)
test_acc = accuracy_score(y_test, y_pred)
logging.info(f"测试集准确率：{test_acc:.4f}")
print(classification_report(y_test, y_pred))

# ------------------ 4. 未知类别预测 ------------------
unknown_df["预测类型"] = best_model.predict(X_unlabeled)
proba = best_model.predict_proba(X_unlabeled)
unknown_df["预测概率(高钾)"] = proba[:, 0]
unknown_df["预测概率(铅钡)"] = proba[:, 1]
unknown_df["置信度"] = proba.max(axis=1)

logging.info("未知类别预测完成。")
print(unknown_df[["文物编号", "预测类型", "预测概率(高钾)", "预测概率(铅钡)", "置信度"]])

# 保存结果
unknown_df.to_csv("glass_classification_results.csv", index=False, encoding="utf-8-sig")
logging.info("结果已保存至 glass_classification_results.csv")

# ------------------ 5. 敏感性分析 ------------------
# 5.1 交叉验证稳定性（用最佳模型再跑一次）
cv = KFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE)
cv_scores = cross_val_score(best_model, X, y, cv=cv)
logging.info(f"5 折交叉验证准确率：{cv_scores}，均值：{cv_scores.mean():.4f} (±{cv_scores.std():.4f})")

# 5.2 特征重要性
importances = best_model.named_steps["clf"].feature_importances_
feat_df = (
    pd.DataFrame({"特征": X.columns, "重要性": importances})
    .sort_values("重要性", ascending=False)
)
plt.figure(figsize=(8, 6))
sns.barplot(x="重要性", y="特征", data=feat_df)
plt.title("特征重要性排序")
plt.tight_layout()
plt.savefig(IMG_DIR / f"feature_importance_{int(time.time())}.png", dpi=300)
plt.close()

# 5.3 输入扰动稳定性
noise_levels = [0.01, 0.05, 0.1]
rng = np.random.default_rng(RANDOM_STATE)
stability = {}
X_unlabeled_scaled = best_model.named_steps["scaler"].transform(X_unlabeled)

for level in noise_levels:
    consistent = 0
    for _ in range(100):
        noise = rng.normal(0, level, X_unlabeled_scaled.shape)
        preds = best_model.named_steps["clf"].predict(X_unlabeled_scaled + noise)
        consistent += np.array_equal(preds, unknown_df["预测类型"])
    stability[level] = consistent / 100
logging.info(f"扰动稳定性：{stability}")

plt.figure(figsize=(6, 4))
plt.bar(stability.keys(), stability.values())
plt.xlabel("噪声水平")
plt.ylabel("稳定性比率")
plt.title("输入扰动稳定性")
plt.tight_layout()
plt.savefig(IMG_DIR / f"noise_stability_{int(time.time())}.png", dpi=300)
plt.close()

# 5.4 预测概率分布
plt.figure(figsize=(8, 5))
for cls in best_model.classes_:
    mask = unknown_df["预测类型"] == cls
    plt.hist(
        unknown_df.loc[mask, f"预测概率({cls})"],
        bins=15, alpha=0.6, label=f"{cls}玻璃"
    )
plt.xlabel("预测概率")
plt.ylabel("频数")
plt.legend()
plt.title("未知样本预测概率分布")
plt.tight_layout()
plt.savefig(IMG_DIR / f"prob_dist_{int(time.time())}.png", dpi=300)
plt.close()

# 5.5 ROC / 阈值分析（二分类）
y_prob_test = best_model.predict_proba(X_test)
y_true_binary = (y_test.values == best_model.classes_[1]).astype(int)
fpr, tpr, thresholds = roc_curve(y_true_binary, y_prob_test[:, 1])
roc_auc = auc(fpr, tpr)


plt.figure(figsize=(6, 5))
plt.plot(fpr, tpr, label=f"AUC = {roc_auc:.3f}")
plt.plot([0, 1], [0, 1], "k--")
plt.xlabel("假正率")
plt.ylabel("真正率")
plt.title("ROC 曲线")
plt.legend()
plt.tight_layout()
plt.savefig(IMG_DIR / f"roc_curve_{int(time.time())}.png", dpi=300)
plt.close()

# 5.6 Bootstrap 置信区间
bootstrap_scores = []
rng = np.random.default_rng(RANDOM_STATE)
for _ in range(1000):
    idx = rng.choice(len(X_test), len(X_test), replace=True)
    score = accuracy_score(y_test.iloc[idx], best_model.predict(X_test.iloc[idx]))
    bootstrap_scores.append(score)
ci_low, ci_high = np.percentile(bootstrap_scores, [2.5, 97.5])
logging.info(f"Bootstrap 95% CI for accuracy: ({ci_low:.4f}, {ci_high:.4f})")

plt.figure(figsize=(6, 4))
plt.hist(bootstrap_scores, bins=30, alpha=0.7)
plt.axvline(ci_low, color="red", linestyle="--")
plt.axvline(ci_high, color="red", linestyle="--")
plt.xlabel("准确率")
plt.ylabel("频数")
plt.title("Bootstrap 准确率分布")
plt.tight_layout()
plt.savefig(IMG_DIR / f"bootstrap_acc_{int(time.time())}.png", dpi=300)
plt.close()

# ------------------ 6. 表面风化细分准确率 ------------------
if "表面风化" in known_df.columns:
    known_df["预测类型"] = best_model.predict(X)
    known_df["预测正确"] = (known_df["类型"] == known_df["预测类型"]).astype(int)
    acc_weather = known_df.groupby("表面风化")["预测正确"].mean()
    logging.info("不同风化状态准确率：\n%s", acc_weather)

    plt.figure(figsize=(6, 4))
    acc_weather.plot(kind="bar")
    plt.title("不同风化状态下的分类准确率")
    plt.ylabel("准确率")
    plt.xticks(rotation=0)
    plt.tight_layout()
    plt.savefig(IMG_DIR / f"acc_by_weathering_{int(time.time())}.png", dpi=300)
    plt.close()

logging.info("全部流程完成！")