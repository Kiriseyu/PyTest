string = "Hello World"

# 检查字符串中每个字符是否为大写
for c in string:
    if c.isupper():
        print(c, "is uppercase")
    else:
        print(c, "is not uppercase")

    # 检查字符串中每个字符是否为小写
for c in string:
    if c.islower():
        print(c, "is lowercase")
    else:
        print(c, "is not lowercase")