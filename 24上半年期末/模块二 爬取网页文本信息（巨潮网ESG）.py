import pandas as pd
import xlrd
import json
import requests
import re

# 需要更改
saving_path = r'G:\ESG报告'
Codelist_path = r"G:\Python课程资料_20230705\Raw DATA\遴选的股票代码\代码.xls"

url = "http://www.cninfo.com.cn/new/data/szse_stock.json"
ret = requests.get(url=url)
ret = ret.content
stock_list = json.loads(ret)["stockList"]

def export_excel(export):
    pf = pd.DataFrame(export)
    order = ['orgId', 'category', 'code', 'pinyin', 'zwjc']
    pf = pf[order]
    columns_map = {
        'orgId': 'orgId（原始ID）',
        'category': 'category（股市类型）',
        'code': 'code（代码）',
        'pinyin': 'pinyin（拼音）',
        'zwjc': 'zwjc（中文简称）'
    }
    pf.rename(columns=columns_map, inplace=True)
    file_path = pd.ExcelWriter('code_list.xlsx')
    pf.fillna(' ', inplace=True)
    assert isinstance(pf.to_excel, object)
    pf.to_excel(file_path, index=False)
    file_path._save()
if __name__ == '__main__':
    export_excel(stock_list)
code_dic = {(it['code']): it['orgId'] for it in stock_list}
class excel_read:
    def __init__(self, excel_path=Codelist_path, encoding='utf-8', index=0):
        self.data = xlrd.open_workbook(excel_path)
        self.table = self.data.sheets()[index]
        self.rows = self.table.nrows
    def get_data(self):
        result = []
        for i in range(self.rows):
            col = self.table.row_values(i)
            print(col)
            result.append(col)
        print(result)
        return result
code_list = []
code_list.extend(excel_read().get_data())

def get_and_download_pdf_file(pageNum, stock, searchkey='', category='', seDate=''):
    url = 'http://www.cninfo.com.cn/new/hisAnnouncement/query'
    pageNum = int(pageNum)
    # 表单数据
    data = {'pageNum': pageNum,
            'pageSize': 30,
            'column': 'szse',
            'tabName': 'fulltext',
            'plate': '',
            'stock': stock,
            'searchkey': searchkey,
            'secid': '',
            'category': category,
            'trade': '',
            'seDate': seDate,
            'sortName': '',
            'sortType': '',
            'isHLtitle': 'true'}
    # 请求头
    headers = {'Accept': '*/*',
               'Accept-Encoding': 'gzip, deflate',
               'Accept-Language': 'zh-CN,zh;q=0.9',
               'Connection': 'keep-alive',
               'Content-Length': '181',
               'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
               'Host': 'www.cninfo.com.cn',
               'Origin': 'http://www.cninfo.com.cn',
               'Referer': 'http://www.cninfo.com.cn/new/commonUrl/pageOfSearch?url=disclosure/list/search',
               'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36',
               'X-Requested-With': 'XMLHttpRequest'}
    # 向页面发出请求
    r = requests.post(url, data=data, headers=headers)
    result = r.json()['announcements']
    for i in result:
        if re.search('摘要', i['announcementTitle']):
            pass
        else:
            title = i['announcementTitle']
            title = title[:4]
            secName = i['secName']
            secName = secName.replace('*', '')
            secCode = i['secCode']
            adjunctUrl = i['adjunctUrl']
            down_url = 'http://static.cninfo.com.cn/' + adjunctUrl
            title1 = 'ESG报告'
            filename = f'{secCode}{secName}{title}{title1}.pdf'
            filepath = saving_path + '\\' + filename
            r = requests.get(down_url)
            with open(filepath, 'wb') as f:
                f.write(r.content)
            print(f'{secCode}{secName}{title}{title1}下载完毕')

# 调用函数，开始下载
Num = len(code_list)
for i in range(0, Num):
    code = code_list[i][0]
    orgId = code_dic[code]
    stock = '{},{}'.format(code, orgId)
    print(stock)
    # 需要更改
    searchkey = 'ESG'
    category = 'category_rcjy_szsh'
    seDate = '2021-01-01~2024-01-01'
    for pageNum in range(1, 3):
        try:
            get_and_download_pdf_file(pageNum, stock, searchkey, category, seDate, )
        except:
            pass