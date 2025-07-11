import urllib.request
import json
import re
import time
import os
def extract_bvid(url):
    match = re.search(r'BV[a-zA-Z0-9]+', url)
    if match:
        return match.group()
    raise ValueError("无法提取BV号")
def get_video_data(bvid):
    api_url = f'https://api.bilibili.com/x/web-interface/view?bvid={bvid}'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }

    try:
        req = urllib.request.Request(api_url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            return data['data'] if data['code'] == 0 else None
    except:
        return None
def get_titles(video_data):
    if not video_data:
        return [], ""
    main_title = video_data.get('title', '').strip()
    pages = video_data.get('pages', [])
    titles = [p.get('part', '').strip() or f"P{i}" for i, p in enumerate(pages, 1)]
    return titles, main_title


def save_titles(titles, main_title):
    if not titles:
        return False
    save_dir = r"C:\Users\26790\Documents\A_Bilibili_Title_SaveFiles"
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
        print(f"创建文件夹: {save_dir}")
    clean_title = re.sub(r'[\\/*?:"<>|]', "", main_title)
    filepath = os.path.join(save_dir, f"{clean_title}.txt")
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            for i, t in enumerate(titles, 1):
                f.write(f"{i}. {t}\n")
        print(f"文件已保存到: {filepath}")
        return filepath
    except Exception as e:
        print(f"保存失败: {e}")
        return False

def main():
    url = 'https://www.bilibili.com/video/BV1yT411H7YK/?spm_id_from=333.337.search-card.all.click&vd_source=4d4c95cdcc465a5d4c0727299878e644'

    try:
        bvid = extract_bvid(url)
        print(f"BV号: {bvid}")

        data = get_video_data(bvid)
        if not data:
            print("获取数据失败")
            return

        titles, main_title = get_titles(data)
        print(f"视频标题: {main_title}")
        print(f"分P数量: {len(titles)}")

        res = save_titles(titles, main_title)
        if res:
            print(f"已保存: {res}")
        else:
            print("保存失败")
    except Exception as e:
        print(f"错误: {e}")


if __name__ == "__main__":
    main()