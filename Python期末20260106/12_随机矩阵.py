import numpy as np
np.random.seed(42)
matrix = np.random.randint(1,51,size=(3,4))
sum_matrix = matrix.sum()
avg_matrix = matrix.mean()
print("3行4列随机矩阵")
print(matrix)
print(f"矩阵所有元素和:{sum_matrix}")
print(f"矩阵所有元素平均值:{avg_matrix:.2f}")