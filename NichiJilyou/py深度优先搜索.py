
grap = {
    "A":["B","C"],
    "B":["A","C","D"],
    "C":["A","B","D","E"],
    "D":["B","C","E","F"],
    "E":["C","D"],
    "F":["D"]
}


def DFS(grap, star):  # DFS算法
    stack = []  # 定义一个栈
    seen = set()  # 建立一个集合，集合就是用来判断该元素是不是已经出现过
    stack.append(star)  # 将任一个节点放入
    seen.add(star)  # 同上
    while (len(stack) > 0):  # 当队列里还有东西时
        ver = stack.pop()  # 取出栈顶元素       !!!!这里也就是与BFS的不同
        notes = grap[ver]  # 查看grep里面的key,对应的邻接点
        for i in notes:  # 遍历邻接点
            if i not in seen:  # 如果该邻接点还没出现过
                stack.append(i)  # 存入stack
                seen.add(i)  # 存入集合
        print(ver)  # 打印栈顶元素


print(DFS(grap,"A"))
