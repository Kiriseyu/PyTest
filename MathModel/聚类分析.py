# 聚类分析又称为群分析，是研究问题的一种多元统计方法。
# 聚类，就是聚集具有相似元素的集合成之为一类。
# 一般来说存在着定性研究和定量研究以及相融汇的三种分析方法。
# 通过选取共同指标，分析元素指标值之间的差距从而达到分类的目的。

# 一般常用样品分类(对样品聚类)和指标分类(对元素聚类)


import numpy as np
from matplotlib import pyplot as plt
from scipy.cluster.hierarchy import dendrogram,linkage
import xlrd as xr
import pandas as pd
from sklearn import preprocessing
from sklearn.cluster import AgglomerativeClustering
file_location="/Users/lifangjian/Desktop/聚类数据.xls"
data=xr.open_workbook(file_location)
sheet = data.sheet_by_index(0)
lie=sheet.ncols
hang=sheet.nrows
#如果第一行是变量名，第一列是不同样本_遍历法
datam=[]
for i in range(1,hang):
    hanglie=[]
    for j in range(1,lie):
        hanglie.append(sheet.cell_value(i,j))
    datam.append(hanglie)
print(datam)
#列表推导式法_得到所有的值，按照行列排列，第一行j个数，第2行j个数。
hanglie=[sheet.cell_value(i,j) for i in range(1,hang) for j in range(1,lie)] #得到所有ij的值
stats = [[sheet.cell_value(r,c) for c in range(1,sheet.ncols)] for r in range(1,sheet.nrows)]#得到所有行列值
stats_frame=pd.DataFrame(stats)
normalizer=preprocessing.scale(stats_frame)
stats_frame_nomalized=pd.DataFrame(normalizer)
print(stats_frame)
print(stats_frame_nomalized)


z=linkage(stats,"average",metric='euclidean',optimal_ordering=True)
print(z)
# average=类平均法，ward=离差平方和法，sin=最短距离法，com=最长距离法，med=中间距离法，cen=重心法，fle=可变类平均法
fig, ax = plt.subplots(figsize=(10,9))
dendrogram(z, leaf_font_size=14) #画图
plt.title("Hierachial Clustering Dendrogram")
plt.xlabel("Cluster label")
plt.ylabel("Distance")
plt.axhline(y=4) #画一条分类线
plt.show()
cluster = AgglomerativeClustering(n_clusters=2, affinity='euclidean', linkage='average')
#linkage模式可以调整,n_cluser可以调整
print(cluster.fit_predict(stats))
plt.figure(figsize=(10, 7))
plt.scatter(stats_frame[0],stats_frame[1], c=cluster.labels_)
plt.show()