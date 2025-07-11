import numpy as np
import matplotlib.pyplot as plt

# 参数设置
POP_SIZE = 200
CROSS_RATE = 0.7
MUTATION_RATE = 0.1
N_GENERATIONS = 300
CITIES = 20  # 城市数量

# 生成随机城市坐标
np.random.seed(42)
cities_coord = np.random.rand(CITIES, 2) * 100


# 计算路径距离
def calc_distance(path):
    total = 0
    for i in range(CITIES - 1):
        total += np.linalg.norm(cities_coord[path[i]] - cities_coord[path[i + 1]])
    total += np.linalg.norm(cities_coord[path[-1]] - cities_coord[path[0]])
    return total


# 初始化种群（随机排列）
def init_population():
    return np.array([np.random.permutation(CITIES) for _ in range(POP_SIZE)])


# 适应度函数（距离越小适应度越高）
def calc_fitness(pop):
    return 1 / int([calc_distance(ind) for ind in pop])


# 顺序交叉（OX）
def crossover(parent1, parent2):
    size = len(parent1)
    start, end = sorted(np.random.choice(size, 2, replace=False))
    child = [-1] * size
    child[start:end] = parent1[start:end]
    ptr = end
    for city in parent2:
        if city not in child:
            if ptr >= size: ptr = 0
            if child[ptr] == -1:
                child[ptr] = city
                ptr += 1
    return np.array(child)


# 交换变异
def mutate(child):
    a, b = np.random.choice(CITIES, 2, replace=False)
    child[a], child[b] = child[b], child[a]
    return child


# 主程序
pop = init_population()
best_distance = []

for _ in range(N_GENERATIONS):
    fitness = calc_fitness(pop)
    best_idx = np.argmax(fitness)
    best_distance.append(1 / fitness[best_idx])

    # 选择（精英保留+轮盘赌）
    elite = pop[best_idx].copy()
    pop = pop[np.random.choice(POP_SIZE, POP_SIZE - 1, p=fitness / fitness.sum())]
    pop = np.vstack([pop, elite])

    # 交叉变异
    new_pop = []
    for i in range(0, POP_SIZE, 2):
        parent1, parent2 = pop[i], pop[i + 1]
        child1, child2 = crossover(parent1, parent2), crossover(parent2, parent1)
        new_pop.append(mutate(child1) if np.random.rand() < MUTATION_RATE else child1)
        new_pop.append(mutate(child2) if np.random.rand() < MUTATION_RATE else child2)

    pop = np.array(new_pop[:POP_SIZE])

# 可视化结果
plt.plot(best_distance)
plt.title("TSP Optimization Process")
plt.xlabel("Generation")
plt.ylabel("Best Distance")
plt.show()
