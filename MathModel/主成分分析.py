from sklearn.decomposition import PCA
import numpy as np

data = np.array([
    [2.5, 2.4, 0.5],
    [0.5, 0.7, 0.3],
    [2.2, 2.9, 0.4],
    [1.9, 2.2, 0.6],
    [3.1, 3.0, 0.7],
    [2.3, 2.7, 0.2]
])

# PCA降维
pca = PCA(n_components=2)
reduced_data = pca.fit_transform(data)

print("降维后数据：\n", reduced_data)
print("解释方差比：", pca.explained_variance_ratio_)
