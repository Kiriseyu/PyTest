import numpy as np
from tensorflow.keras import layers, models

# 参数设置
POP_SIZE = 20
CROSS_RATE = 0.7
MUTATION_RATE = 0.2
N_GENERATIONS = 10
INPUT_SHAPE = (28, 28, 1)
NUM_CLASSES = 10


# 初始化种群（编码方式：每层类型+神经元数量）
def init_population():
    return np.array([
        [np.random.choice(['Conv2D', 'Dense'], p=[0.7, 0.3]),
         np.random.randint(16, 256)]
        for _ in range(POP_SIZE)
    ])


# 解码为Keras模型
def decode(individual):
    model = models.Sequential()
    model.add(layers.InputLayer(INPUT_SHAPE))

    for layer_type, units in individual:
        if layer_type == 'Conv2D':
            model.add(layers.Conv2D(units, (3, 3), activation='relu'))
            model.add(layers.MaxPooling2D((2, 2)))
        elif layer_type == 'Dense':
            model.add(layers.Flatten())
            model.add(layers.Dense(units, activation='relu'))

    model.add(layers.Dense(NUM_CLASSES, activation='softmax'))
    model.compile(optimizer='adam', loss='sparse_categorical_cross-entropy', metrics=['accuracy'])
    return model


# 适应度函数（使用验证集准确率）
def calc_fitness(pop, x_val, y_val):
    return [decode(ind).evaluate(x_val, y_val, verbose=0)[1] for ind in pop]


# 主程序（需准备验证数据X_val, y_val）
# ... 此处应加载验证数据 ...

pop = init_population()
best_accuracy = []

for _ in range(N_GENERATIONS):
    fitness = calc_fitness(pop, X_val, y_val)
    best_accuracy.append(np.max(fitness))

    # 选择（精英保留）
    elite_idx = np.argmax(fitness)
    elite = pop[elite_idx].copy()
    pop = pop[np.argsort(fitness)[-POP_SIZE // 2:]]  # 保留前50%

    # 交叉变异
    new_pop = [elite]
    while len(new_pop) < POP_SIZE:
        parent1, parent2 = pop[np.random.choice(len(pop), 2)]
        if np.random.rand() < CROSS_RATE:
            cross_point = np.random.randint(1, len(parent1))
            child = np.vstack([parent1[:cross_point], parent2[cross_point:]])
        else:
            child = parent1.copy()

        if np.random.rand() < MUTATION_RATE:
            mutation_point = np.random.randint(len(child))
            if mutation_point == 0:
                child[0] = np.random.choice(['Conv2D', 'Dense'])
            else:
                child[1] = np.random.randint(16, 256)

        new_pop.append(child)

    pop = np.array(new_pop[:POP_SIZE])

# 输出最优结构
best_idx = np.argmax(best_accuracy)
print(f"最优准确率：{best_accuracy[best_idx]:.4f}")
print("最优网络结构：")
for layer in pop[best_idx]:
    print(f"{layer[0]} - {layer[1]} units")
