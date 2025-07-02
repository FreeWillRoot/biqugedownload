fuckerdownload

小说网址：https://www.smskjg.com/，如果你要换成其他小说网站，合理替换掉代码的这部分就行了：

```
 dl_elements = soup.find_all('dl')
        for dl in dl_elements:
            for dd in dl.find_all('dd'):
                link = dd.find('a')
                if link and link.get('href'):
                    chapter_links.append(link.get('href'))
```

使用方法：python fuckerdownload.py -t 30 -u "https://www.smskjg.com/sms/75852/"
or
python fuckerdownload.py
