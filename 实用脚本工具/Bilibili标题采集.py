import urllib
import urllib.request
import re
import gzip
from io import BytesIO
import time

def get_html(url):
    """
    发送请求并返回获取到的HTML数据(字符串)
    支持gzip解压处理
    """
    header = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Accept-Encoding': 'gzip, deflate',  # 声明支持gzip压缩
        'Connection': 'keep-alive',
    }
    try:
        # 使用传入的url创建一个请求
        request = urllib.request.Request(url, headers=header)
        # 发送请求并得到响应，添加超时设置
        response = urllib.request.urlopen(request, timeout=10)
        # 获取响应头信息
        info = response.info()
        # 检查是否使用了gzip压缩
        if info.get('Content-Encoding') == 'gzip':
            # 读取压缩数据并解压
            compressed_data = response.read()
            buf = BytesIO(compressed_data)
            with gzip.GzipFile(fileobj=buf) as f:
                html_data = f.read().decode('utf-8')
        else:
            # 直接读取并解码
            html_data = response.read().decode('utf-8')
        return html_data
    except urllib.error.URLError as e:
        print(f"URL错误: {e.reason}")
        return None
    except urllib.error.HTTPError as e:
        print(f"HTTP错误: {e.code} - {e.reason}")
        return None
    except Exception as e:
        print(f"请求失败: {e}")
        return None


def save_titles(data, filename='黑马Java教程(上).txt'):
    if not data:
        print("没有数据可保存！")
        return
    try:
        with open(filename, 'w', encoding='utf-8') as file:
            # 写入文件头信息
            file.write(f"B站视频标题采集 - {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            file.write("=" * 50 + "\n\n")
            # 写入所有标题
            for i, title in enumerate(data, 1):
                # 清理标题中的空白字符
                clean_title = title.strip()
                file.write(f"{i}. {clean_title}\n")
                print(f'第{i}个标题写入成功！')
            file.write(f"\n总共采集到 {len(data)} 个标题")
        print(f"\n文件保存成功：{filename}")
    except IOError as e:
        print(f"文件写入错误: {e}")
def get_titles(html):
    if not html:
        return []
    # 原始正则表达式（保留以兼容原有格式）
    pattern1 = re.compile('<div class="title-txt">(.*?)</div>', re.S)
    titles1 = re.findall(pattern1, html)
    # 如果没找到，尝试其他可能的B站标题格式
    if not titles1:
        # 尝试匹配分P标题的另一种常见格式
        pattern2 = re.compile('<span class="part-name">(.*?)</span>', re.S)
        titles2 = re.findall(pattern2, html)
        if titles2:
            return titles2
        # 尝试匹配视频列表标题
        pattern3 = re.compile('<li class="part-item".*?title="(.*?)"', re.S)
        titles3 = re.findall(pattern3, html)
        if titles3:
            return titles3
        print("未找到匹配的标题，可能页面结构已更新")
        return []
    return titles1

def main():
    """主函数"""
    print("B站视频标题采集工具")
    print("=" * 30)

    # 要采集的视频URL
    url = 'https://www.bilibili.com/video/BV13W4y127Ey/?vd_source=4d4c95cdcc465a5d4c0727299878e644'

    print(f"正在采集: {url}")
    print("请稍候...\n")

    # 发送请求并获取数据
    html = get_html(url)

    if html:
        # 匹配出我们需要的数据
        titles = get_titles(html)

        if titles:
            print(f"成功找到 {len(titles)} 个标题\n")
            # 将数据保存到本地
            save_titles(titles)
        else:
            print("未找到任何标题，可能页面结构已更新")
            # 可选：保存HTML供调试
            with open('debug.html', 'w', encoding='utf-8') as f:
                f.write(html)
            print("已保存HTML到debug.html供分析")
    else:
        print("获取网页内容失败")
    # input('\n按回车键退出...')


if __name__ == '__main__':
    main()