import requests
from bs4 import BeautifulSoup
import csv
import os
from urllib.parse import quote
import hashlib

# 输入你想要查询的日期
print("请输入你想要查询的日期：")
date = input()

url = f"https://www.billboard.com/charts/hot-100/{date}/"

# 设置请求头，确保 headers 是字典类型
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
}

# 发送请求
response = requests.get(url, headers=headers)

if response.status_code == 200:
    # 解析页面内容
    soup = BeautifulSoup(response.text, "html.parser")
    
    # 找到包含歌曲和歌手信息的条目
    entries = soup.find_all('li', class_='o-chart-results-list__item')
    
    # 打开 CSV 文件写入数据
    with open(f'billboard_hot_100_cleaned_{date}.csv', mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['歌曲名', '歌手'])

        # 遍历每个条目
        for entry in entries:
            # 查找歌曲名和歌手名
            song_name_tag = entry.find('h3', class_='c-title')
            artist_name_tag = entry.find('span', class_='c-label')

            if song_name_tag and artist_name_tag:
                song_name = song_name_tag.text.strip()
                artist_name = artist_name_tag.text.strip()

                # 排除无效的数据
                if song_name != "未知歌曲名" and artist_name not in ["-", "NEW", "1", "95", "25", "64"]:
                    print(f"歌曲名: {song_name}, 歌手: {artist_name}")
                    writer.writerow([song_name, artist_name])
else:
    print(f"请求失败，HTTP 状态码: {response.status_code}")

# bing查找图片
BING_IMAGE_SEARCH_URL = "https://www.bing.com/images/search?q={query}"

# 模拟浏览器的请求头
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0"
}

# 搜索并获取图片 URL
def get_image_url_bing(song_name, artist_name):
    query = quote(f"{song_name} {artist_name} album cover")
    search_url = BING_IMAGE_SEARCH_URL.format(query=query)

    try:
        response = requests.get(search_url, headers=HEADERS)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        # 提取图片 URL
        img_tags = soup.find_all("img")
        for img in img_tags:
            img_url = img.get("src")
            if img_url and img_url.startswith("http"):
                return img_url
        return None
    except Exception as e:
        print(f"搜索图片失败: {e}")
        return None

# 下载图片并保存
def download_image(img_url, file_path):
    try:
        img_data = requests.get(img_url, headers=HEADERS).content
        with open(file_path, 'wb') as img_file:
            img_file.write(img_data)
        print(f"图片已保存: {file_path}")
    except Exception as e:
        print(f"下载图片失败: {e}")

# 确保保存图片的文件夹存在
output_folder = f'Static/album_covers_{date}'
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# 读取 CSV 文件并处理每个条目
with open(f'billboard_hot_100_cleaned_{date}.csv', mode='r', encoding='utf-8') as file:
    reader = csv.reader(file)
    next(reader)  # 跳过表头

    # 遍历每一行，获取歌曲名和歌手
    for index, row in enumerate(reader, start=1):
        song_name = row[0]
        artist_name = row[1]

        print(f"正在搜索: {song_name} - {artist_name}")

        # 获取图片 URL
        img_url = get_image_url_bing(song_name, artist_name)

        if img_url:
            # 创建文件名：歌手名字 - 歌曲名字
            file_name = f"{artist_name} - {song_name}.jpg"
            file_name = file_name.replace("/", "_")  # 替换文件名中的特殊字符
            file_name = file_name.replace("?", "_")  # 替换问号等特殊字符
            file_path = os.path.join(output_folder, file_name)
            download_image(img_url, file_path)
        else:
            print(f"未找到 {song_name} - {artist_name} 的专辑封面")

file_path = f'billboard_hot_100_cleaned_{date}.csv'
if not os.path.exists(file_path):
    print(f"文件 {file_path} 不存在。")
else:
    print(f"文件 {file_path} 存在。")

