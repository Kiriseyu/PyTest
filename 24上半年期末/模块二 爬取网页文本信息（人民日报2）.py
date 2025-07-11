# 爬取指定开始日期和结束日期的新闻列表
import requests
from bs4 import BeautifulSoup
import time
import random
import json
import datetime

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36'
}


def get_page_data(year, month, day, col_url, col_title):
    month2 = str(month).zfill(2)
    day2 = str(day).zfill(2)
    url = f'http://paper.people.com.cn/rmrb/html/{year}-{month2}/{day2}/{col_url}'

    res = requests.get(url, headers=headers)
    res.encoding = 'utf-8'
    soup = BeautifulSoup(res.text, 'html.parser')
    ul = soup.find(class_='news-list')
    lis = ul.find_all('li')
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

    res = requests.get(url, headers=headers)
    res.encoding = 'utf-8'
    soup = BeautifulSoup(res.text, 'html.parser')
    div0 = soup.find(class_='swiper-container')
    divs = div0.find_all('div')
    result = []
    for div in divs:
        a = div.a
        href = a['href']
        if href[0:2] == './':
            href = href[2:]
        title = a.get_text()
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
        print(year, month, day, col['col_url'], col['col_title'])
        data = get_page_data(year, month, day, col['col_url'], col['col_title'])
        time.sleep(random.randint(2, 4))
        result.extend(data)

    month2 = str(month).zfill(2)
    day2 = str(day).zfill(2)
    file = f'data_list/{year}-{month2}-{day2}.json'
    with open(file, 'w', encoding='utf-8') as fb:
        json.dump(result, fb)


def get_days_data(begin_date, end_date):
    date = begin_date
    while date < end_date:
        print('当前日期是', date)
        year = date.year
        month = date.month
        day = date.day
        get_day_data(year, month, day)
        date = date + datetime.timedelta(days=1)


if __name__ == '__main__':
    begin_date = datetime.datetime(year=2022, month=11, day=3)
    end_date = datetime.datetime(year=2022, month=11, day=6)
    get_days_data(begin_date, end_date)

