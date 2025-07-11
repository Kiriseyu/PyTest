import matplotlib.pyplot as plt
import networkx as nx
import matplotlib

# 设置 Matplotlib 使用支持中文的字体
matplotlib.rcParams['font.sans-serif'] = ['SimHei']  # 指定默认字体
matplotlib.rcParams['axes.unicode_minus'] = False
# 创建一个有向图
G = nx.DiGraph()

# 添加节点（实体）
G.add_node("车队", label="车队\n车队号PK\n车队名")
G.add_node("司机", label="司机\n司机编号PK\n姓名\n电话")
G.add_node("车辆", label="车辆\n牌照号PK\n厂家\n出厂日期")
G.add_node("聘用", label="聘用\n车队号FK\n司机编号FK\n聘期")
G.add_node("拥有", label="拥有\n车队号FK\n牌照号FK")
G.add_node("使用", label="使用\n司机编号FK\n牌照号FK\n使用日期\n公里数")

# 添加边（关系）
G.add_edge("车队", "聘用", label="聘用")
G.add_edge("聘用", "司机", label="")  # 这里的label可以省略，因为已经在聘用节点上标注了
G.add_edge("车队", "拥有", label="拥有")
G.add_edge("拥有", "车辆", label="")  # 同上
G.add_edge("司机", "使用", label="使用")
G.add_edge("使用", "车辆", label="")  # 同上

# 设置节点位置（这一步是可选的，但可以帮助你更好地控制图的布局）
pos = {
    "车队": (0, 2),
    "司机": (2, 2),
    "车辆": (1, 0),
    "聘用": (0, 1),
    "拥有": (1, 1),
    "使用": (2, 1)
}

# 绘制图形
plt.figure(figsize=(10, 6))
nx.draw(G, pos, with_labels=True, node_size=3000, node_color="lightblue", font_size=10, font_weight="bold", arrows=True, arrowstyle='-|>', arrowsize=20)

# 添加节点上的详细标签（因为直接在节点上添加多行文本可能不太美观，所以这里使用注释的方式）
for node in G.nodes():
    plt.text(pos[node][0], pos[node][1] + 0.3, G.nodes[node]['label'], fontsize=10, ha='center')

# 隐藏坐标轴
plt.axis('off')

# 显示图形
plt.show()
