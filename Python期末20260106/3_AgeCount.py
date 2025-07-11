import numpy as np
age_array = np.random.randint(0,101,size = 30)
print(age_array)
teenager = 0# 青少年
middle = 0#中年
elderly = 0#老年
for age in age_array:
    if age < 30:
        teenager += 1
    elif age >= 30 and age < 60:
        middle += 1
    else:
        elderly += 1
print()