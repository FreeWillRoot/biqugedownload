# coding=utf-8

import sys
import getopt
import requests
import time
from urllib import parse
import random
from lxml import etree
from concurrent.futures import ThreadPoolExecutor

#默认配置选项
THREADS=50
BOOKNAME=''
AUTHOR=''
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

def fetchbook():
    global AUTHOR,BOOKNAME,USER_AGENT
    url = 'https://www.biquge5200.com/modules/article/search.php?searchkey=%s'%(BOOKNAME,)
    response = requests.get(url.format(parse.quote_plus(BOOKNAME)), headers = {'User-Agent':random.choice(USER_AGENT)}, timeout=10)
    response = etree.HTML(response.content.decode('gbk'))
    list = response.xpath("//table/tr/td[@class='odd']/a[text()='%s']" % BOOKNAME)
    if list != []:
        for li in list:
            print('已找到小说:',li.xpath("text()")[0],'          ',li.xpath("../../td[@class='odd'][2]/text()")[0])
        url = response.xpath("//table/tr/td[@class='odd'][text()='%s']/../td[@class='odd']/a[text()='%s']/@href" % (AUTHOR, BOOKNAME))
        if url:
            distribution(url[0])
        else:
            print('抱歉，笔趣阁内暂时找不到您搜索的书籍')
            exit()
    else:
        print('抱歉，笔趣阁内暂时找不到您搜索的书籍')
        exit()

def downloadTxt(url,name):
    #开始下载小说
    global USER_AGENT
    response = requests.get(url, headers = {'User-Agent':random.choice(USER_AGENT)}, timeout=10)
    response = etree.HTML(response.text)
    txt = response.xpath("//*[@id='content']/p/text()") or response.xpath("//div[@class='text']/text()")
    print(name)
    print(txt)
    if len(txt) == 0:
        #此处爬取太快分析返回值发现间歇空白，所以肯定是时间被限制了，只能重复请求。
        print(url)
        time.sleep(1)
        downloadTxt(url,name)
    else:
        with open('book_list/{}.txt'.format(name), 'w') as f:
            f.write(name)
            f.write(''.join(txt).replace('　　', ''))
            f.close()
    

def distribution(url):
    #url链接分发
    global THREADS
    res = requests.get(url, headers = {'User-Agent':random.choice(USER_AGENT)}, timeout=10)
    res = etree.HTML(res.text)
    chapter_url = res.xpath("//*[@id='list']/dl/dd/a/@href")[9:]
    chapter_name = res.xpath("//*[@id='list']/dl/dd/a/text()")[9:]
    # 获取了所有的url和名称
    with ThreadPoolExecutor(int(THREADS)) as executor:
        print('共下发下载任务:',len(chapter_url))
        for url,name in zip(chapter_url,chapter_name):
            executor.submit(downloadTxt,url,name)


def main():
    global BOOKNAME,AUTHOR,THREADS
    args = getopt.getopt(sys.argv[1:],'-h-t:-b:-a:',[])
    for key,value in args[0]:
        if key == "-h":
            print('''
            用法: python3 fuckerdownload.py [OPTIONS]
            -h: 帮助信息
            -t: 线程数，默认50
            -b: 书籍名字
            -a: 作者名字
            '''
            )
            continue
        if key == '-t':
            THREADS=value
        if key == "-b":
            BOOKNAME = value
            continue
        if key == "-a":
            AUTHOR = value
            continue
    fetchbook()


if __name__ == "__main__":
    main()
