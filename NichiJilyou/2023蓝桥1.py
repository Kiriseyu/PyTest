def find_2023(s):
    o = s.find('2')
    if o == -1:
        return False

    t = s.find('0',o + 1)
    if t == -1:
        return False

    tt = s.find('2',t + 1)
    if tt == -1:
        return False

    f = s.find('3',tt + 1)
    if f == -1:
        return False


es = 0
for i in range(12345678,98765433,1):
    w = find_2023(str(i))
    if w is False:
        es += 1
print(es)
