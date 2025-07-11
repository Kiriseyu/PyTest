import random
nums = [random.randint(0, 99) for _ in range(50)]
for num in nums:
    if num % 2 != 0:
        print(num, end = ' ')
