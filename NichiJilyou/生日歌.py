def happy1():
    print("Happy Birthday to You!")
def happy2(name):
    happy1()
    happy1()
    print(f"Happy Birthday to You 亲爱的{name}同学!")
    happy1()
def main():
    happy2("张三")
    happy2("李四")

if __name__ == "__main__":
    main()