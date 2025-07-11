# 冒泡排序:(5,4,1,2,8)
def mao_pao(a):
    for i in range(1,len (a)):
        for j in range(len(a)-i):
            if a[j] > a[j + 1]:
                a[j], a[j + 1] = a[j +1], a[j]
    return a
b = [2, 11, 10, 5, 4, 13, 9, 7, 8, 1, 12, 3, 6, 15, 14]
print(mao_pao(b))

# python内置排序
# 使用sort()方法排序
numbers = [3, 1, 4, 1, 5, 9, 2, 6, 5, 3, 5]
numbers.sort()
print(numbers)  # 输出：[1, 1, 2, 3, 3, 4, 5, 5, 5, 6, 9]

# 使用sorted()函数排序
numbers = [3, 1, 4, 1, 5, 9, 2, 6, 5, 3, 5]
sorted_numbers = sorted(numbers)
print(sorted_numbers)  # 输出：[1, 1, 2, 3, 3, 4, 5, 5, 5, 6, 9]

# 选择排序
def selection_sort(arr):
    for i in range(len(arr)):
        min_index = i
        for j in range(i + 1, len(arr)):
            if arr[min_index] > arr[j]:
                min_index = j
        arr[i], arr[min_index] = arr[min_index], arr[i]
    return arr
numbers = [2, 6, 5 ,3, 4, 7, 8, 1, 1]
print(numbers)

# 归并排序
def merge_sort(arr):
    if len(arr) <= 1:
        return arr
    mid = len(arr) // 2
    left_arr = arr[:mid]
    right_arr = arr[mid:]
    left_arr = merge_sort(left_arr)
    right_arr = merge_sort(right_arr)
    return merge(left_arr, right_arr)


def merge(left_arr, right_arr):
    result = []
    i = j = 0
    while i < len(left_arr) and j < len(right_arr):
        if left_arr[i] <= right_arr[j]:
            result.append(left_arr[i])
            i += 1
        else:
            result.append(right_arr[j])
            j += 1
    result += left_arr[i:]
    result += right_arr[j:]
    return result