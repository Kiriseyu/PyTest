import os
py_count = 0
current_dir = os.getcwd()
print("当前目录下的.py文件")
for file in os.listdir(current_dir):
    if file.endswith(".py"):
        print(file)
        py_count += 1
print(f"后缀为'.py'的文件个数：{py_count}")
