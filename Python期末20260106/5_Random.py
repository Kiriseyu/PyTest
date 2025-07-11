import random
numbers = []
for i in range(10):
    num = random.randint(1,20)
    numbers.append(num)
print(numbers)
unique_numbers = []
for num in numbers:
    if num not in unique_numbers:
        unique_numbers.append(num)
print(unique_numbers)
for i in range(len(unique_numbers)):
    for j in range(i+1,len(unique_numbers)):
        if unique_numbers[i] < unique_numbers[j]:
            temp = unique_numbers[i]
            unique_numbers[i] = unique_numbers[j]
            unique_numbers[j] = temp
print(unique_numbers)