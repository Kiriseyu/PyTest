import xlwt
import pandas as pd
import jieba
from simhash import Simhash

# jaccard
def jaccard(model, reference):
    terms_reference = jieba.cut(reference)
    terms_model = jieba.cut(model)
    grams_reference = set(terms_reference)
    grams_model = set(terms_model)
    temp = 0
    for i in grams_reference:
        if i in grams_model:
            temp = temp +1
    fenmu = len(grams_model) + len(grams_reference) - temp
    try:
        jaccard_coefficient = float(temp / fenmu)
    except ZeroDivisionError:
        print(model, reference)
        return 0
    else:
        return jaccard_coefficient
# 需要修改
df_data1 = pd.read_excel('G:\Python课程资料_20230705\Raw DATA\人民日报新闻\人民日报新闻示例2.xlsx')
a = []
for i in range(0,len(df_data1)-1):        # 两两比较，需要个数-1次
    row1 = df_data1.loc[i]
    s1 = row1['内容']
    row2 = df_data1.loc[i+1]
    s2 = row2['内容']
    jac = jaccard(s1, s2)
    a.append(jac)
    s3 = row1['版面']
    print(s3)
book = xlwt.Workbook(encoding='utf-8',style_compression=0)
# 需要修改
sheet = book.add_sheet('新闻',cell_overwrite_ok=True)
for i in range(0,len(a)):
    sheet.write(i,0,a[i])
# 需要修改
savepath = 'G:/jaccard.xls'
book.save(savepath)

# simhash
def simhash_demo(text_a, text_b):
    a_simhash = Simhash(text_a)
    b_simhash = Simhash(text_b)
    max_hashbit = max(len(bin(a_simhash.value)), len(bin(b_simhash.value)))
    distince = a_simhash.distance(b_simhash)
    similar = 1 - distince / max_hashbit
    return similar
b=[]
for i in range(0,len(df_data1)-1):
    row1 = df_data1.loc[i]
    s1 = row1['内容']
    row2 = df_data1.loc[i+1]
    s2 = row2['内容']
    sim = simhash_demo(s1, s2)
    b.append(sim)
    s3 = row1['版面']
    print(s3)
book = xlwt.Workbook(encoding='utf-8',style_compression=0)
# 需要修改
sheet = book.add_sheet('新闻',cell_overwrite_ok=True)
for i in range(0,len(b)):
    sheet.write(i,0,b[i])
# 需要修改
savepath = 'G:/simhash.xls'
book.save(savepath)
