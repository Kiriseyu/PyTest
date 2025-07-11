import numpy as np

# 参数设置
POP_SIZE = 100
CROSS_RATE = 0.8
MUTATION_RATE = 0.05
N_GENERATIONS = 50
CAPACITY = 50  # 背包容量

# 物品数据（价值，重量）
ITEMS = np.array([
    (60, 10), (100, 20), (120, 30),
    (80, 5), (40, 8), (150, 40)
])


# 初始化种群（二进制编码）
def init_population():
    return np.random.randint(0, 2, (POP_SIZE, len(ITEMS)))


# 计算适应度
def calc_fitness(pop):
    values = (pop * ITEMS[:, 0]).sum(axis=1)
    weights = (pop * ITEMS[:, 1]).sum(axis=1)
    penalty = (weights > CAPACITY) * 1e4  # 惩罚超重个体
    return values - penalty


# 主程序
pop = init_population()
best_fitness = []

for _ in range(N_GENERATIONS):
    fitness = calc_fitness(pop)
    best_fitness.append(np.max(fitness))

    # 选择（锦标赛选择）
    selected = []
    for _ in range(POP_SIZE):
        candidates = pop[np.random.choice(POP_SIZE, 3)]
        selected.append(candidates[np.argmax(calc_fitness(candidates))])
    pop = np.array(selected)

    # 交叉（单点交叉）
    new_pop = []
    for i in range(0, POP_SIZE, 2):
        parent1, parent2 = pop[i], pop[i + 1]
        if np.random.rand() < CROSS_RATE:
            cross_point = np.random.randint(1, len(ITEMS) - 1)
            parent1[cross_point:], parent2[cross_point:] = parent2[cross_point:].copy(), parent1[cross_point:].copy()
        new_pop.extend([parent1, parent2])

    # 变异
    for i in range(len(new_pop)):
        if np.random.rand() < MUTATION_RATE:
            new_pop[i][np.random.randint(len(ITEMS))] ^= 1  # 按位异或实现翻转

    pop = np.array(new_pop[:POP_SIZE])

# 输出最优解
best_idx = np.argmax(best_fitness)
print(f"最优解出现在第{best_idx}代")
print(f"最大价值：{best_fitness[best_idx]}")
print("选中物品：", np.where(pop[best_idx] == 1)[0] + 1)
