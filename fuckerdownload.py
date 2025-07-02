# coding=utf-8

import sys
import getopt
import requests
import time
import random
import os
from lxml import etree
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor

# 默认配置选项
THREADS = 50
BOOK_URL = 'https://www.smskjg.com/sms/75852/'
USER_AGENT = [
"Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_8; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50",
"Mozilla/5.0 (Windows; U; Windows NT 6.1; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50",
"Mozilla/5.0 (Windows NT 10.0; WOW64; rv:38.0) Gecko/20100101 Firefox/38.0",
"Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; .NET4.0C; .NET4.0E; .NET CLR 2.0.50727; .NET CLR 3.0.30729; .NET CLR 3.5.30729; InfoPath.3; rv:11.0) like Gecko",
"Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0)",
"Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0)",
"Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0)",
"Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1)",
"Mozilla/5.0 (Macintosh; Intel Mac OS X 10.6; rv:2.0.1) Gecko/20100101 Firefox/4.0.1",
"Mozilla/5.0 (Windows NT 6.1; rv:2.0.1) Gecko/20100101 Firefox/4.0.1",
"Opera/9.80 (Macintosh; Intel Mac OS X 10.6.8; U; en) Presto/2.8.131 Version/11.11",
"Opera/9.80 (Windows NT 6.1; U; en) Presto/2.8.131 Version/11.11",
"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_0) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11",
"Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Maxthon 2.0)",
"Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; TencentTraveler 4.0)",
"Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)",
"Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; The World)",
"Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Trident/4.0; SE 2.X MetaSr 1.0; SE 2.X MetaSr 1.0; .NET CLR 2.0.50727; SE 2.X MetaSr 1.0)",
"Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; 360SE)",
"Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Avant Browser)",
"Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)",
"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.125 Safari/537.36"
]

# 创建一个字典来存储章节内容
chapter_contents = {}

def get_chapter_list():
    """获取小说的所有章节链接"""
    global BOOK_URL, USER_AGENT
    
    headers = {'User-Agent': random.choice(USER_AGENT)}
    response = requests.get(BOOK_URL, headers=headers, timeout=10)
    response.encoding = 'utf-8'
    
    # 使用BeautifulSoup解析HTML
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # 查找章节列表
    chapter_links = []
    chapter_names = []
    
    # 根据用户提供的信息，查找id为list的元素下的dd标签
    list_div = soup.find('div', id='list')
    if list_div:
        for dd in list_div.find_all('dd'):
            link = dd.find('a')
            if link and link.get('href'):
                chapter_links.append(link.get('href'))
                chapter_names.append(link.text.strip())
    else:
        print("未找到id为list的元素，尝试查找其他可能的章节列表结构")
        # 尝试查找其他可能的章节列表结构
        dl_elements = soup.find_all('dl')
        for dl in dl_elements:
            for dd in dl.find_all('dd'):
                link = dd.find('a')
                if link and link.get('href'):
                    chapter_links.append(link.get('href'))
                    chapter_names.append(link.text.strip())
    
    return chapter_links, chapter_names

def download_chapter(url, name, index):
    """下载单个章节的内容"""
    global USER_AGENT, chapter_contents
    
    try:
        headers = {'User-Agent': random.choice(USER_AGENT)}
        response = requests.get(url, headers=headers, timeout=10)
        response.encoding = 'utf-8'
        
        # 使用BeautifulSoup解析HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 查找章节内容
        content_div = soup.find('div', id='content')
        if not content_div:
            content_div = soup.find('div', class_='content')
        
        if content_div:
            # 提取文本内容
            content = content_div.get_text('\n', strip=True)
            print(f"已下载: {name}")
            
            # 将内容存储到字典中，使用索引作为键以保持顺序
            chapter_contents[index] = (name, content)
            return True
        else:
            print(f"无法找到章节内容: {name}, URL: {url}")
            return False
    except Exception as e:
        print(f"下载章节失败: {name}, URL: {url}, 错误: {e}")
        time.sleep(2)  # 出错后等待一段时间再重试
        return download_chapter(url, name, index)  # 递归重试

def save_full_novel():
    """将所有章节内容保存为一个完整的文件"""
    global chapter_contents
    
    # 从URL中提取书名或使用默认名称
    book_name = "novel"
    
    # 创建保存目录
    if not os.path.exists('novels'):
        os.makedirs('novels')
    
    # 保存文件名
    filename = f"novels/{book_name}.txt"
    
    print(f"正在将所有章节合并到文件: {filename}")
    
    # 按索引排序章节
    sorted_chapters = [chapter_contents[i] for i in sorted(chapter_contents.keys())]
    
    # 写入文件
    with open(filename, 'w', encoding='utf-8') as f:
        # 写入每个章节
        for name, content in sorted_chapters:
            f.write(f"\n{name}\n\n")
            f.write(content)
            f.write("\n\n")
    
    print(f"下载完成! 文件已保存为: {filename}")

def download_novel():
    """使用多线程下载小说"""
    global THREADS, BOOK_URL
    
    print(f"开始下载小说")
    print(f"小说网址: {BOOK_URL}")
    
    # 获取章节列表
    chapter_links, chapter_names = get_chapter_list()
    
    if not chapter_links:
        print("未找到任何章节链接，请检查网址是否正确")
        return
    
    print(f"共找到 {len(chapter_links)} 个章节")
    
    # 使用多线程下载章节
    with ThreadPoolExecutor(max_workers=int(THREADS)) as executor:
        futures = []
        for i, (link, name) in enumerate(zip(chapter_links, chapter_names)):
            print(f"原始链接: {link}")
            # 如果链接不是完整URL，则添加域名
            if not link.startswith('http'):
                if link.startswith('//'):
                    link = f"https:{link}"
                elif link.startswith('/'):
                    link = f"https://www.smskjg.com{link}"
                else:
                    link = f"https://www.smskjg.com/{link}"
            print(f"处理后的链接: {link}")
            
            # 提交下载任务
            future = executor.submit(download_chapter, link, name, i)
            futures.append(future)
        
        # 等待所有任务完成
        for future in futures:
            future.result()
    
    # 保存完整小说
    save_full_novel()

def main():
    global BOOK_URL, THREADS
    
    args = getopt.getopt(sys.argv[1:], '-h-t:-u:', ['help', 'threads=', 'url='])[0]
    
    for key, value in args:
        if key in ('-h', '--help'):
            print('''
            用法: python3 fuckerdownload.py [OPTIONS]
            -h, --help: 显示帮助信息
            -t, --threads: 线程数，默认50
            -u, --url: 小说网址 (默认: https://www.smskjg.com/sms/75852/)
            ''')
            return
        if key in ('-t', '--threads'):
            THREADS = value
        if key in ('-u', '--url'):
            BOOK_URL = value
    
    download_novel()

if __name__ == "__main__":
    main()