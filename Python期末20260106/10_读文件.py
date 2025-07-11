count = 0
try:
    with open("test.txt","r",encoding = "utf-8") as f:
        for line_num,line in enumerate(f,1):
            if "Python" in line:
                count += 1
    print(f"包含Python的行数:{count}")
except FileNotFoundError:
    print("文件不存在")