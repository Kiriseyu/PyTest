import numpy as np
import matplotlib.pyplot as plt
plt.rcParams['font.sans-serif'] = ['SimHei']  # 指定默认字体为SimHei
plt.rcParams['axes.unicode_minus'] = False



# 定义x1, x2, y的值（注意：这里将v修改为y，并用列表形式定义）
x1 = np.array(
    [-0.05,0.25,0.60,0,0.25,0.20,0.15,0.05,-0.15,0.15,0.20,0.10,0.40,0.45,0.35,0.30,0.50,0.50,0.40,-0.05,-0.05,-0.10,0.20,0.10,0.50,0.60,-0.05,0,0.05,0.55])
x2 = np.array(
    [5.50,6.75,7.25,5.50,7.00,6.50,6.75,5.25,5.25,6.00,6.50,6.25,7.00,6.90,6.80,6.80,7.10,7.00,6.80,6.50,6.25,6.00,6.50,7.00,6.80,6.80,6.50,5.75,5.80,6.80])
y = np.array(
    [7.38,8.51,9.52,7.50,9.33,8.28,8.75,7.87,7.10,8.00,7.89,8.15,9.10,8.86,8.90,8.87,9.26,9.00,8.75,7.95,7.65,7.27,8.00,8.50,8.75,9.21,8.27,7.67,7.93,9.26])
# print(len(x1))
# print(len(x2))
# print(len(y))

# 线性回归
A1 = np.polyfit(x1, y, 1)
yy1 = np.polyval(A1, x1)

# 二次回归
A2 = np.polyfit(x2, y, 2)
x5 = np.linspace(5, 7.25, num=46)  # 生成等间距的x值
yy2 = np.polyval(A2, x5)

# 绘制两个子图
plt.figure(figsize=(10, 5))  # 创建一个新的图形窗口，并设置大小

# 第一个子图
plt.subplot(1, 2, 1)
plt.plot(x1, y, 'o', label='Data')
plt.plot(x1, yy1, '-', label='Linear Fit')
plt.title('图1: y对x1的线性回归图')
plt.xlabel('x1')
plt.ylabel('y')
plt.legend()  # 添加图例

# 第二个子图
plt.subplot(1, 2, 2)
plt.plot(x2, y, 'o', label='Data')
plt.plot(x5, yy2, '-', label='Quadratic Fit')
plt.title('图 2: y对x2的二次回归图')
plt.xlabel('x2')
plt.ylabel('y')
plt.legend()  # 添加图例

# 显示图形
plt.tight_layout()  # 调整子图布局
plt.show()

# 如果你想保存图像，可以使用下面的代码
# plt.savefig('my_plot.png')
