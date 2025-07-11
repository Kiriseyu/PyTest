import numpy as np

# 参数设置
POP_SIZE = 100
CROSS_RATE = 0.9
MUTATION_RATE = 0.1
N_GENERATIONS = 200
JOBS = 5  # 作业数量
MACHINES = 3  # 机器数量

# 加工时间矩阵（job, machine）
PROCESS_TIME = np.array([
    [2, 1, 3],
    [4, 2, 1],
    [3, 4, 2],
    [1, 3, 4],
    [2, 4, 3]
])


# 计算完成时间（基于排列编码）
def calc_makespan(schedule):
    machine_time = np.zeros(MACHINES)
    job_completion = np.zeros(JOBS)

    for job in schedule:
        for m in range(MACHINES):
            start_time = max(machine_time[m], job_completion[job])
            machine_time[m] = start_time + PROCESS_TIME[job, m]
            job_completion[job] = machine_time[m]

    return machine_time.max()


# 初始化种群（随机排列）
def init_population():
    return np.array([np.random.permutation(JOBS) for _ in range(POP_SIZE)])


# 适应度函数
def calc_fitness(pop):
    return 1 / np.array([calc_makespan(ind) for ind in pop])


# 部分映射交叉（PMX）
def crossover(parent1, parent2):
    size = len(parent1)
    a, b = sorted(np.random.choice(size, 2, replace=False))
    child = parent1.copy()
    child[a:b + 1] = parent2[a:b + 1]

    # 修复重复值
    for i in range(a, b + 1):
        if child[i] not in parent2[a:b + 1]:
            val = child[i]
            idx = np.where(parent1 == val)[0][0]
            while a <= idx <= b:
                val = parent1[idx]
                idx = np.where(parent1 == val)[0][0]
            child[idx] = val

    return child


# 交换变异
def mutate(child):
    a, b = np.random.choice(JOBS, 2, replace=False)
    child[a], child[b] = child[b], child[a]
    return child


# 主程序
pop = init_population()
best_makespan = []

for _ in range(N_GENERATIONS):
    fitness = calc_fitness(pop)
    best_makespan.append(1 / fitness.max())

    # 选择（锦标赛选择）
    selected = []
    for _ in range(POP_SIZE):
        candidates = pop[np.random.choice(POP_SIZE, 3)]
        selected.append(candidates[np.argmax(calc_fitness(candidates))])
    pop = np.array(selected)

    # 交叉变异
    new_pop = []
    for i in range(0, POP_SIZE, 2):
        parent1, parent2 = pop[i], pop[i + 1]
        child1, child2 = crossover(parent1, parent2), crossover(parent2, parent1)
        new_pop.append(mutate(child1) if np.random.rand() < MUTATION_RATE else child1)
        new_pop.append(mutate(child2) if np.random.rand() < MUTATION_RATE else child2)

    pop = np.array(new_pop[:POP_SIZE])

# 输出最优调度方案
best_idx = np.argmax(calc_fitness(pop))
print(f"最优调度顺序：{pop[best_idx]}")
print(f"最小完成时间：{calc_makespan(pop[best_idx])}")
