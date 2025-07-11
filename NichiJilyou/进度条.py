from time import sleep
from tqdm import tqdm
for i in tqdm(range(1, 500)):
    for a in range(500):
        if a < 500:
            a += 1
            print(a)
        if a >= 500:
            continue
sleep(0.01)
sleep(0.5)
