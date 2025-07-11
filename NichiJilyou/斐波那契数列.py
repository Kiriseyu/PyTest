def fibonacci(n):
    if n <= 0:
        return []
    elif n == 1:
        return [0]
    elif n == 2:
        return [0, 1]
    fib_list = [0, 1]
    for i in range(2, n):
        fib_list.append(fib_list[i - 1] + fib_list[i - 2])
    return fib_list

def main():
    while True:
        try:
            n = int(input())
            if n < 0:
                print("ERROR")
            else:
                break
        except ValueError:
            print("ERROR")
    result = fibonacci(n)
    print(result)

if __name__ == "__main__":
    main()