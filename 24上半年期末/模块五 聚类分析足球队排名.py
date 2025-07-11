import pandas as pd
from sklearn.cluster import KMeans
from sklearn import preprocessing

df = pd.read_excel('G:\Python课程资料_20230705\Raw DATA\足球排名\足球排名.xlsx')
df.info()
df.head()

# 获取三列特征值
train_x = df[["2019年国际排名","2018世界杯","2015亚洲杯"]]
df_02 = pd.DataFrame(train_x)

# 建立模型  设置为3个簇
k_model = KMeans(n_clusters=3)

# 数据归一化
min_max_scaler = preprocessing.MinMaxScaler()
train_x = min_max_scaler.fit_transform(train_x)

# 训练模型
k_model.fit(train_x)
predict_y = k_model.predict(train_x)

df["聚类"] = predict_y
df.to_excel('聚类.xlsx',index=False)
