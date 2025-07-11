money = 10000
#for循环给员工发工资
for i in range(1, 21):
    import random
    score = random.randint(1, 10)

    if score < 5:
        print(f"{i}绩效分{score},不发")
        continue

    if money >= 1000:
        money -= 1000
        print(f"{i}满足，发放，余额{money}")
    else:
        print(f"当前余额{money},不足以发工资")
        break
