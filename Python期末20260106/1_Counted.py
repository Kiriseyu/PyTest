#统计大小写
s = input()
upper_count = 0
lower_count = 0
digit_count = 0
other_count = 0
for char in s:
    if char.isupper():
        upper_count += 1
    elif char.islower():
        lower_count += 1
    elif char.isdigit():
        digit_count += 1
    else:
        other_count += 1
print(upper_count, lower_count, digit_count, other_count)