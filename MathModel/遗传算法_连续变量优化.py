import numpy as np

# 遗传算法参数
POP_SIZE = 100  # 种群大小
GENE_LENGTH = 5  # 基因长度（二进制编码）
CROSS_RATE = 0.8  # 交叉概率
MUTATION_RATE = 0.1  # 变异概率
N_GENERATIONS = 50  # 迭代次数


# 初始化种群（随机生成二进制编码）
def init_population():
    return np.random.randint(0, 2, (POP_SIZE, GENE_LENGTH))


# 将二进制基因解码为整数
def decode(population):
    return population.dot(1 << np.arange(GENE_LENGTH - 1, -1, -1))


# 计算适应度（目标函数为 f(x) = x^2）
def calc_fitness(population):
    x = decode(population)
    return x ** 2


# 轮盘赌选择（按适应度比例选择）
def select(population, fitness):
    idx = np.random.choice(
        np.arange(POP_SIZE),
        size=POP_SIZE,
        replace=True,
        p=fitness / fitness.sum()  # 概率与适应度成正比
    )
    return population[idx]


# 单点交叉
def crossover(parent, pop):
    if np.random.rand() < CROSS_RATE:
        # 随机选择另一个个体进行交叉
        idx = np.random.randint(0, POP_SIZE)
        cross_point = np.random.randint(1, GENE_LENGTH - 1)
        parent[cross_point:] = pop[idx, cross_point:]
    return parent


# 基因变异
def mutate(child):
    for point in range(GENE_LENGTH):
        if np.random.rand() < MUTATION_RATE:
            child[point] = 1 - child[point]  # 0变1，1变0
    return child


# 主算法流程
def genetic_algorithm():
    pop = init_population()
    best_history = []

    for generation in range(N_GENERATIONS):
        # 计算适应度
        fitness = calc_fitness(pop)
        best_idx = np.argmax(fitness)
        best_history.append(decode(pop[best_idx]))

        # 打印当前最优解
        if generation % 10 == 0:
            print(f"Gen {generation}: Best x = {decode(pop[best_idx])}, f(x) = {fitness[best_idx]}")

        # 选择
        pop = select(pop, fitness)

        # 生成新一代种群
        new_population = []
        for parent in pop:
            # 交叉
            child = crossover(parent.copy(), pop)
            # 变异
            child = mutate(child)
            new_population.append(child)

        pop = np.array(new_population)

    return best_history


# 运行算法并可视化结果（需要matplotlib）
import matplotlib.pyplot as plt

best_x_history = genetic_algorithm()
plt.plot(best_x_history)
plt.title("Best Solution Evolution")
plt.xlabel("Generation")
plt.ylabel("Best x Value")
plt.show()