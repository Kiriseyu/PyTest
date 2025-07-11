import math

def main():
    while True:
        # try:
            r = float(input())
            if r < 0:
                print("请半径不能为负数，请重新输入半径值")
                continue
            break
        # except ValueError:
        #     print("Input Error")
    S = math.pi * r ** 2
    L = 2 * math.pi * r
    # print(f"面积 S = {S:.2f}")
    # print(f"周长 L = {L:.2f}")
    print(S)
    print(L)
if __name__ == "__main__":
    main()
