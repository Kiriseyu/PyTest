# 根据列表，下载具体网页
import requests
import time
import random
import json
import os


headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36'
}
fold = 'data_list'  # 这里写的是相对路径，需要py文件和此文件夹同级

def get_files():
    files = os.listdir(fold)
    # print(files)
    return files

def read_file(file_name):
    path = os.path.join(fold, file_name)   # 路径拼接，即fold文件夹+file_name文件名
    # print(path)
    with open(path, 'r', encoding='utf-8') as fb:
        result = json.load(fb)
    # print(result)
    return result

def get_cont(year, month, day, href):
    month2 = str(month).zfill(2)
    day2 = str(day).zfill(2)
    url = f'http://paper.people.com.cn/rmrb/html/{year}-{month2}/{day2}/{href}'
    # print(url)
# ----------------------------直接复制即可------------------------------
    res = requests.get(url, headers=headers)
    res.encoding = 'utf-8'
    # soup = BeautifulSoup(res.text, 'html.parser')
# ----------------------------直接复制即可------------------------------
#     print(soup)
    # 建议保留网页，而不是只保留文本
    fold = 'data_cont'
    fold2 = f'{year}-{month2}-{day2}'
    fold3 = os.path.join(fold, fold2)
    if not os.path.exists(fold3):
        os.mkdir(fold3)
    file_name = os.path.join(fold3, href)
    # print(file_name)
    with open(file_name, 'w', encoding='utf-8') as fb:
        # fb.write(soup.text)
        fb.write(res.text)            # 保存带标签

def get_all():
    files = get_files()
    for file in files:
        records = read_file(file)
        for record in records:
            print(record['year'], record['month'], record['day'], record['href'])     # 设置进度条
            get_cont(record['year'], record['month'], record['day'], record['href'])
            # time.sleep(random.randint(2, 4))         # 太快容易触发反爬虫机制

if __name__ == '__main__':
    # files = get_files()
    # file = files[0]
    # print(file)
    # data = read_file(file)
    # record = data[0]
    # print(record)
    # get_cont(record['year'], record['month'], record['day'], record['href'])
    get_all()