import docx                            # 用以读取word文件
import jieba                           # 用以分词的一个工具
import pandas as pd                    # 用以将结果输出到excel文件
from collections import Counter        # 用以统计词频
import math                            # 用以计算对数

## 高频词统计
# 需要更改
fn = r'G:\Python课程资料_20230705\Raw DATA\人民日报新闻\人民日报新闻示例1.docx'
document = docx.Document(fn)
content = ' '.join([para.text for para in document.paragraphs])
len_content = len(content)
seg_list = jieba.cut(content,cut_all=False)
# seg_list = [word for word in seg_list]
seg_list = [word for word in seg_list if len(word)>1]
counter = Counter(seg_list)
df = pd.DataFrame(list(counter.items()),columns=['word','count'])
# df.sort_values(by='count',inplace=True)
df.sort_values(by='count',ascending=False,inplace=True)
# 需要更改
df.to_excel('人民日报新闻示例1高频词统计.xlsx',index=False)

## 利用词典计算词频
# 政治&经济
import re
def get_stop_dict(file):
    text = open(file,encoding="utf-8")
    word_list = []
    for c in text:
        c = re.sub('\n| \r','',c)
        word_list.append(c)
    return word_list
# 需要更改
use_file1 = r'G:\Python课程资料_20230705\字典\政治.txt'
use_words1 = get_stop_dict(use_file1)
seg_list1 = [word for word in seg_list if len(word)>1 and word in use_words1]
counter1 = Counter(seg_list1)
df1 = pd.DataFrame(list(counter1.items()),columns=['word','count'])
df1.sort_values(by='count',ascending=False,inplace=True)
# 需要更改
df1.to_excel('人民日报新闻_政治.xlsx',index=False)
df_data1 = pd.read_excel('人民日报新闻_政治.xlsx')
politics = 0
for i in range(0,len(df1)):
    row1 = df_data1.loc[i]
    s1 = row1['count']
    politics=politics+s1
    print(politics)
print(politics)

# 需要更改
use_file1 = r'G:\Python课程资料_20230705\字典\经济.txt'
use_words1 = get_stop_dict(use_file1)
seg_list1 = [word for word in seg_list if len(word)>1 and word in use_words1]
counter1 = Counter(seg_list1)
df1 = pd.DataFrame(list(counter1.items()),columns=['word','count'])
df1.sort_values(by='count',ascending=False,inplace=True)
# 需要更改
df1.to_excel('人民日报新闻_经济.xlsx',index=False)
df_data1 = pd.read_excel('人民日报新闻_经济.xlsx')
economy = 0
for i in range(0,len(df1)):
    row1 = df_data1.loc[i]
    s1 = row1['count']
    economy=economy+s1
    print(economy)
print(economy)


# 2.正负面
# 正面
use_file2 = r'G:\Python课程资料_20230705\字典\正面.txt'
use_words2 = get_stop_dict(use_file2)
seg_list2 = [word for word in seg_list if len(word)>1 and word in use_words2]
counter2 = Counter(seg_list2)
df2 = pd.DataFrame(list(counter2.items()),columns=['word','count'])
df2.sort_values(by='count',ascending=False,inplace=True)
# 需要更改
df2.to_excel('人民日报新闻_正面.xlsx',index=False)
df_data2 = pd.read_excel('人民日报新闻_正面.xlsx')
positive = 0
for i in range(0,len(df2)):
    row1 = df_data2.loc[i]
    s1 = row1['count']
    positive = positive+s1
print(positive)
# 负面
use_file3 = r'G:\Python课程资料_20230705\字典\负面.txt'
use_words3 = get_stop_dict(use_file3)
seg_list3 = [word for word in seg_list if len(word)>1 and word in use_words3]
counter3 = Counter(seg_list3)
df3 = pd.DataFrame(list(counter3.items()),columns=['word','count'])
df3.sort_values(by='count',ascending=False,inplace=True)
# 需要更改
df3.to_excel('人民日报新闻_负面.xlsx',index=False)
df_data3 = pd.read_excel('人民日报新闻_负面.xlsx')
negative = 0
for i in range(0,len(df3)):
    row1 = df_data3.loc[i]
    s1 = row1['count']
    negative = negative+s1
print(negative)

# 3.可读性
# words_per_sentence + percent_of_complex_words
# 需要更改
use_file4 = r'G:\Python课程资料_20230705\字典\次常用字.txt'
use_words4 = get_stop_dict(use_file4)
seg_list4=[]
for i in content:
    if i in use_words4:
        seg_list4.append(i)
percent_of_complex_words = len(seg_list4) / len_content
content1 = ""
for i in content:
    rp0 = i.replace("。", "@")
    rp1 = rp0.replace("？", "@")
    rp2 = rp1.replace("！", "@")
    content1 += rp2
sentence = content1.count("@")
print(sentence)
words_per_sentence = len_content / sentence
print(words_per_sentence)
FOG = (words_per_sentence + percent_of_complex_words)*0.4
ucwords = 1 / math.log(len(seg_list4)+1)
char0 = 1 / math.log(len_content)
print(FOG, ucwords, char0)
