t, n = map(int, input().split())
# map对input内容做映射
for i in range(t):
    # i循环T行
    ls = list(map(int, input().split()))
    # 创建输入列表并对列表做映射
    one = 0
    # 1队的初始值为0
    zero = 0
    # 0队的初始值为0
    for j in ls:
        # j在列表中循环
        if j == 0:
            # 当j==0时
            zero += 1
            # 0队+=1（人）
        if j == 1:
            # 当j== 1时
            one += 1
            # 1队+= 1
    print(abs(one-zero))
# 输出1队-0队的绝对值
