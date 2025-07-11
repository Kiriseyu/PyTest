n, q = map(int, input().split())
books = [input() for i in range(n)]
for _ in range(q):
    len, code = input().split()
    code = [int(i) for i in books if i[-int(len):] == code]
    print(min(code))if code != []else print(-1)
