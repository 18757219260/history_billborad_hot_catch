import streamlit as st
import os
import pandas as pd
import hashlib
from PIL import Image
import matplotlib.pyplot as plt
from collections import Counter
import numpy as np
#C:\Users\19339\album_web\app.py
# 读取流派并统计出现次数，排除"未知"
def get_genre_counter(date):
    """
    获取指定日期的流派分布并统计出现次数。
    """
    genre_counter = Counter()  # 初始化计数器

    try:
        # 读取指定日期的流派数据文件
        df = pd.read_csv(f'billboard_with_genres_{date}.csv', encoding='utf-8')
    except FileNotFoundError:
        # 如果文件不存在，提示用户
        st.write(f"文件 'billboard_with_genres_{date}.csv' 未找到。请确保文件存在。")
        return genre_counter

    # 过滤掉流派为"未知"的行
    df = df[df['流派'] != '未知']

    # 统计每个流派出现的次数
    for genre in df['流派']:
        genre_counter[genre] += 1

    return genre_counter

# 绘制流派分布的雷达图
def plot_radar_chart(genres, counts):
    """
    绘制流派分布的雷达图。
    """
    # 计算每个流派的角度
    angles = np.linspace(0, 2 * np.pi, len(genres), endpoint=False).tolist()
    counts = np.concatenate((counts, [counts[0]]))  # 闭合雷达图
    angles += angles[:1]  # 添加第一个角度使图形封闭

    # 创建雷达图
    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))
    ax.fill(angles, counts, color='skyblue', alpha=0.5)  # 填充多边形
    ax.plot(angles, counts, color='blue', linewidth=2)  # 绘制边线

    # 绘制点并设置样式
    for i, (angle, count) in enumerate(zip(angles, counts)):
        color = 'red' if i == len(counts) - 1 else 'blue'  # 最后一个点为红色
        size = 80 if i == len(counts) - 1 else 40  # 最后一个点更大
        ax.scatter(angle, count, c=color, s=size, zorder=5)

    # 添加数据标签
    for angle, count in zip(angles, counts):
        ax.text(angle, count + 10, f'{int(count)}', ha='center', va='center', fontsize=20, color='black')

    # 设置刻度和标签
    ax.set_yticklabels([])  # 移除雷达图纵坐标标签
    ax.set_xticks(angles[:-1])  # 设置X轴为流派
    ax.set_xticklabels(genres, fontsize=20, rotation=45)

    # 设置标题
    ax.set_title("流派分布雷达图", fontsize=30, pad=20)
    st.pyplot(fig)  # 在Streamlit中显示图表

# 获取指定日期的歌手和歌曲信息
def get_artist_and_songs(date):
    """
    获取指定日期的歌手和歌曲信息。
    """
    try:
        # 读取指定日期的CSV文件
        df = pd.read_csv(f'billboard_hot_100_cleaned_{date}.csv', encoding='utf-8')
    except FileNotFoundError:
        # 如果文件不存在，提示用户
        st.write(f"文件 'billboard_hot_100_cleaned_{date}.csv' 未找到。请确保文件存在。")
        return []

    # 返回歌手和歌曲的元组列表
    artist_and_songs = list(zip(df['歌手'], df['歌曲名']))
    return artist_and_songs

# 获取指定日期的歌手出现次数
def get_artist_counter(date):
    """
    统计指定日期歌手的出现次数。
    """
    artist_counter = Counter()

    try:
        # 读取指定日期的CSV文件
        df = pd.read_csv(f'billboard_hot_100_cleaned_{date}.csv', encoding='utf-8')
    except FileNotFoundError:
        # 如果文件不存在，提示用户
        st.write(f"文件 'billboard_hot_100_cleaned_{date}.csv' 未找到。请确保文件存在。")
        return artist_counter

    # 统计每个歌手出现的次数
    for artist_name in df['歌手']:
        artist_counter[artist_name] += 1

    return artist_counter

# 显示指定歌手的专辑封面
def display_artist_covers(date, artist_name):
    """
    显示指定日期和歌手的专辑封面。
    """
    covers_folder = f"Static/album_covers_{date}"  # 专辑封面文件夹路径

    if not os.path.exists(covers_folder):
        # 如果封面文件夹不存在，提示用户
        st.write(f"未找到日期为 {date} 的专辑封面文件夹。请检查路径和文件是否正确。")
        return

    try:
        # 读取指定日期的CSV文件
        df = pd.read_csv(f'billboard_hot_100_cleaned_{date}.csv', encoding='utf-8')
    except FileNotFoundError:
        # 如果文件不存在，提示用户
        st.write(f"文件 'billboard_hot_100_cleaned_{date}.csv' 未找到。请确保文件存在。")
        return

    # 查找匹配的封面
    artist_covers = []
    unique_hashes = set()
    song_names = {}

    for file_name in os.listdir(covers_folder):
        if artist_name.lower() in file_name.lower():
            file_path = os.path.join(covers_folder, file_name)

            # 使用哈希值避免重复图片
            with open(file_path, 'rb') as f:
                file_hash = hashlib.md5(f.read()).hexdigest()

            if file_hash not in unique_hashes:
                unique_hashes.add(file_hash)
                artist_covers.append(file_path)
                # 提取歌曲名
                song_name = file_name.split('-', 1)[1].replace(".jpg", "").strip()
                song_names[file_path] = song_name

    if not artist_covers:
        # 如果未找到封面，提示用户
        st.write(f"未找到歌手 {artist_name} 的任何专辑封面。")
        return

    # 计算需要的子图行数
    num_images = len(artist_covers)
    rows = (num_images // 4) + (1 if num_images % 4 != 0 else 0)

    # 创建子图并显示封面
    fig, axes = plt.subplots(rows, 4, figsize=(16, 4 * rows))
    axes = axes.flatten()

    for i, cover_path in enumerate(artist_covers):
        img = Image.open(cover_path)
        axes[i].imshow(img)
        axes[i].axis('off')  # 隐藏坐标轴
        song_name = song_names.get(cover_path, "未知歌曲名")
        axes[i].set_title(song_name, fontsize=25, fontweight='bold', color='red', pad=10)

    for j in range(i + 1, len(axes)):  # 隐藏多余的子图
        axes[j].axis('off')

    plt.tight_layout()
    st.pyplot(fig)

# Streamlit界面主函数
def display_dashboard():
    """
    显示 Streamlit 仪表板。
    """
    st.title("Billboard Hot 100 数据展示大屏")

    # 用户输入日期
    date = st.text_input("请输入日期 (格式: 如2003-09-10):")

    if date:
        show_chart_option = st.radio("请选择榜单显示范围:", ("显示全部", "显示前50位", "显示前10位"))

        # 获取歌手出现次数
        artist_counter = get_artist_counter(date)
        if artist_counter:
            plt.rcParams['font.sans-serif'] = ['SimHei']  # 设置中文字体支持
            
            st.subheader(f"{date} 歌手出现次数条形图")

            # 提取歌手名字和次数
            artists, counts = zip(*artist_counter.most_common(10))
            
            # 绘制横向条形图
            plt.figure(figsize=(50, 30))
            bars = plt.barh(artists, counts, color='skyblue')

            # 添加数据标签
            for bar in bars:
                plt.text(bar.get_width() - 0.5, bar.get_y() + bar.get_height() / 2,
                         f'{int(bar.get_width())}', va='center', ha='left', fontsize=65)

            plt.xlabel("出现次数", fontsize=70)
            plt.ylabel("歌手", fontsize=70)
            plt.title("歌手出现次数 (前10名)", fontsize=60)

            plt.gca().invert_yaxis()  # 从上到下显示
            plt.xticks(fontsize=60)
            plt.yticks(fontsize=60)

            st.pyplot(plt)

        # 获取并展示流派雷达图
        genre_counter = get_genre_counter(date)
        if genre_counter:
            plt.figure(figsize=(50, 30))
            genres, counts = zip(*genre_counter.most_common(10))  # 获取前10个流派和它们的出现次数
            
            st.subheader(f"{date} 流派雷达图")
            plot_radar_chart(genres, counts)

        # 显示歌手和歌曲信息
        artist_and_songs = get_artist_and_songs(date)
        if artist_and_songs:
            st.subheader("Billboard Hot 100 歌手及歌曲")

            # 根据用户选择显示范围
            if show_chart_option == "显示全部":
                col1, col2 = st.columns(2)
                with col1:
                    for i in range(50):
                        artist, song = artist_and_songs[i]
                        st.write(f"{i+1}. {artist} - {song}")

                with col2:
                    for i in range(50, 100):
                        artist, song = artist_and_songs[i]
                        st.write(f"{i+1}. {artist} - {song}")

            elif show_chart_option == "显示前50位":
                col1, col2 = st.columns(2)
                with col1:
                    for i in range(25):
                        artist, song = artist_and_songs[i]
                        st.write(f"{i+1}. {artist} - {song}")

                with col2:
                    for i in range(25, 50):
                        artist, song = artist_and_songs[i]
                        st.write(f"{i+1}. {artist} - {song}")

            elif show_chart_option == "显示前10位":
                col1, col2 = st.columns(2)
                with col1:
                    for i in range(5):
                        artist, song = artist_and_songs[i]
                        st.write(f"{i+1}. {artist} - {song}")

                with col2:
                    for i in range(5, 10):
                        artist, song = artist_and_songs[i]
                        st.write(f"{i+1}. {artist} - {song}")

        # 用户输入歌手名字查看专辑封面
        artist_name = st.text_input("请输入歌手名字查看专辑封面:")
        if artist_name:
            display_artist_covers(date, artist_name)

# 主程序入口
if __name__ == "__main__":
    display_dashboard()  # 运行主函数
