import requests
import csv
import time
date=input('请输入你要查询的日期：')
def get_genre_from_apple_music(song_name, artist_name):
    """
    从 Apple Music API 获取歌曲流派
    """
    base_url = "https://itunes.apple.com/search"
    params = {
        "term": f"{song_name} {artist_name}",  # 搜索关键词
        "entity": "musicTrack",               # 搜索实体类型
        "limit": 1,                           # 限制结果数量
        "country": "us",                      # 国家区域
    }
    
    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()  # 检查请求是否成功
        results = response.json().get("results", [])
        if results:
            # 提取流派信息
            return results[0].get("primaryGenreName", "未知")
        else:
            return "未知"
    except Exception as e:
        print(f"获取流派失败: {e}")
        return "未知"

def add_genre_to_csv(input_csv, output_csv):
    """
    为 CSV 文件中的歌曲添加流派信息，并保存到新的 CSV 文件中
    """
    try:
        with open(input_csv, mode='r', encoding='utf-8') as infile, \
             open(output_csv, mode='w', newline='', encoding='utf-8') as outfile:
            
            reader = csv.reader(infile)
            writer = csv.writer(outfile)
            
            # 读取表头并添加 "流派" 列
            headers = next(reader)
            writer.writerow(headers + ["流派"])
            
            # 遍历每行，获取歌曲名和歌手，并添加流派
            for row in reader:
                song_name = row[0]
                artist_name = row[1]
                print(f"正在获取流派: {song_name} - {artist_name}")
                genre = get_genre_from_apple_music(song_name, artist_name)
                writer.writerow(row + [genre])
                print(f"流派: {genre}")
                
                
        print(f"处理完成，结果已保存到 {output_csv}")
    except Exception as e:
        print(f"处理 CSV 文件失败: {e}")

# 示例调用
input_csv = f"billboard_hot_100_cleaned_{date}.csv"  # 输入的歌曲 CSV 文件
output_csv = f"billboard_with_genres_{date}.csv"     # 输出的文件名

add_genre_to_csv(input_csv, output_csv)