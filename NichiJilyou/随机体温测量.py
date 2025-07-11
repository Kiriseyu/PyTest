def temperature():
    import random
    x = random.randint(0, 42)
    if 37.5 >= x >= 36.5:
        print(f"实时体温是{x},体温正常")
    else:
        print(f"实时体温是{x},体温异常")


temperature()


# random随机浮点数0.0--1.0范围内
def ax():
    import random
    print(random.random())


ax()
# gauss(mu,sigma)正态分布
# expovariate(lambd) 指数分布
# uniform() 返回随机浮点数
