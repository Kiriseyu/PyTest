
# 准备工作：快捷键+安装包
 # Ctrl+/ 快速注释和取消注释
# shift+alt+e 可以单独运行选中的几行命令

# 安装数据包 requests和bs4
# bs4 主要用于搜索和抓取网页信息 file-setting
# 要求 自行安装jieba 包并截图上传学习通（示例已经给出）

# 导入工具包
# 使用import导入整个模块：
# • import 模块名 [as 别名] • 使用模块中某个特定的函数：
# • from 模块名 import 函数名 [as 别名]
# 在程序中导入包
# import requests
# from bs4 import BeautifulSoup

# 获取网页、分析网页
# requests模块
# • requests.get()：获取html的主要方法。
# • requests.post()：向html网页提交post请求的方法。
# • requests.status_code：http请求的返回状态，若为200则表示请求成功。
# • requests.text：http响应内容的字符串形式，即返回的页面内容。
# • requests.content：http响应内容的二进制形式，常常用该方法爬取图片、视频等数据。
# • response.encoding：设定html的编码类型。如果使用response.text得到的html中文是乱码
# 的，则需要设定文本编码类型。


# 请求头设定 （因为许多网站设置了反爬虫机制） 摁住F12键或者fn+f12 调用出开发者工具

# 爬取某日01版的新闻列表
import requests
from bs4 import BeautifulSoup

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36 Edg/125.0.0.0'
}

url = 'http://paper.people.com.cn/rmrb/html/2024-06/12/nbs.D110000renmrb_01.htm'    # 人民日报网址
res = requests.get(url, headers=headers)
res.encoding = 'utf-8' # 为了防止乱码
soup = BeautifulSoup(res.text, 'html.parser')      # res.text是网页内容，'html.parser'是固定常用的解析器

# print(soup)  #shift +Alt+e  运行代码

# 点击Ctrl+F  看内容是否被爬取下来

div = soup.find(class_='news-list')
# print(div)
# 点击Ctrl+F  看内容是否被爬取下来

lis = div.find_all('li')
# for li in lis:
#     print(li)
#     print('-' * 100)      # 分割线，方便观察

# for li in lis:
#     a = li.a              # 进一步分解
#     href = a['href']
#     title = a.get_text()
#     print(href, title)
#     print('-' * 100)


result = []              # 空列表装结果
for li in lis:
    a = li.a
    href = a['href']
    title = a.get_text()
    dic = {
        'href': href,
        'title': title
    }
    result.append(dic)
print(result)
#
# 添加注释：学号：202302911060157 姓名：张曜宇
#  取消注释 学号：202302911060157 姓名：张曜宇

# 爬取某日版面信息
import requests
from bs4 import BeautifulSoup

# ----------------------------直接复制即可------------------------------
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36 Edg/125.0.0.0'
}

url = 'http://paper.people.com.cn/rmrb/html/2022-11/08/nbs.D110000renmrb_01.htm'
res = requests.get(url, headers=headers)
res.encoding = 'utf-8'
soup = BeautifulSoup(res.text, 'html.parser')
# ----------------------------直接复制即可------------------------------
divs = soup.find_all(class_='swiper-slide')
# for div in divs:
#     print(div)
#     print('-' * 100)
result=[]
for div in divs:
    a = div.a
    href = a['href']
    title = a.get_text()
    dic = {
        'href': href,
        'title': title
    }
    result.append(dic)
print(result)


# 爬取某日所有版面的新闻列表
import requests
from bs4 import BeautifulSoup
import time
import random
import json
import pandas as pd

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'
}

def get_page_data(year, month, day, col_url, col_title):         # 额外添加，是把它封装起来
    month2 = str(month).zfill(2)                            # 传入数字，补齐为2位字符串
    day2 = str(day).zfill(2)
    url = f'http://paper.people.com.cn/rmrb/html/{year}-{month2}/{day2}/{col_url}'
    print(url)
# ----------------------------直接复制即可------------------------------
    res = requests.get(url, headers=headers)
    res.encoding = 'utf-8'
    soup = BeautifulSoup(res.text, 'html.parser')
    ul = soup.find(class_='news-list')
    lis = ul.find_all('li')
# ----------------------------直接复制即可------------------------------
    result = []
    for li in lis:
        a = li.a
        dic = {
            'href': a['href'],
            'title': a.get_text(),
            'year': year,
            'month': month,
            'day': day,
            'col_url': col_url,
            'col_title': col_title,
        }
        result.append(dic)
    return result

def get_page_cols(year, month, day):
    month2 = str(month).zfill(2)
    day2 = str(day).zfill(2)
    url = f'http://paper.people.com.cn/rmrb/html/{year}-{month2}/{day2}/nbs.D110000renmrb_01.htm'
# ----------------------------直接复制即可------------------------------
    res = requests.get(url, headers=headers)
    res.encoding = 'utf-8'
    soup = BeautifulSoup(res.text, 'html.parser')
# ----------------------------直接复制即可------------------------------
    div0 = soup.find(class_= 'swiper-container')
    divs = div0.find_all('div')
    result = []
    for div in divs:
        a = div.a
        href = a['href']
        title = a.get_text()
        if href[0:2]=='./':
            href = href[2:]
        # print(href, title)
        # print(div.a)
        # print('-' * 100)
        dic = {
            'col_url': href,
            'col_title': title,
        }
        result.append(dic)
    return result

def get_day_data(year, month, day):
    cols = get_page_cols(year, month, day)
    result = []
    for col in cols:
        print(year, month ,day, col['col_url'], col['col_title'])          # 设置进度条
        data = get_page_data(year, month, day, col['col_url'], col['col_title'])
        time.sleep(random.randint(2,4))            #每获取一次休息2~4秒，防止搞崩网页或触发反爬虫
        # print(data)
        # print('-' * 100)
        result.extend(data)        # 是列表的拼接，不能用append

    month2 = str(month).zfill(2)
    day2 = str(day).zfill(2)
    file = f'data_list/{year}-{month2}-{day2}.json'
    with open(file, 'w', encoding='utf-8') as fb:
        json.dump(result, fb)

def export_excel(export):
    pf = pd.DataFrame(export)            # 将字典列表转换为DataFrame
    order = ['href', 'title', 'year', 'month', 'day', 'col_url', 'col_title']    # 指定字段顺序
    pf = pf[order]                                                               # 指定字段顺序
    # 将列名替换为中文
    columns_map = {
        'href': 'href（标签）',
        'title': 'title（题目）',
        'year': 'year（年）',
        'month': 'month（月）',
        'day': 'day（日）',
        'col_url': 'col_url（栏目标签）',
        'col_title': 'col_title（栏目题目）',
    }
    pf.rename(columns=columns_map, inplace=True)
    file_path = pd.ExcelWriter('list.xlsx')                    # 指定生成的Excel表格名称
    pf.fillna(' ', inplace=True)                               # 替换空单元格
    pf.to_excel(file_path,  index=False)                       # 输出
    file_path._save()                                          # 保存表格


if __name__ == '__main__':
    year = 2022
    month = 11
    day = 8
    # col_url = 'nbs.D110000renmrb_01.htm'
    # col_title = '01版：要闻'
    # result = get_page_data(year, month, day, col_url, col_title)
    # print(result)

    # result = get_page_cols(year, month, day)

    get_day_data(year, month, day)

    month2 = str(month).zfill(2)
    day2 = str(day).zfill(2)
    with open(f'data_list/{year}-{month2}-{day2}.json') as f:
        data = json.load(f)
    export_excel(data)

    # print(result)



