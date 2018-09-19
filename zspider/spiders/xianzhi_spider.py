# -*- coding: utf-8 -*-

import scrapy
from .. import items
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from zspider import util
import os

# 闲置二手爬虫
class XianzhiSpider(scrapy.spiders.Spider):
    name = 'xianzhi'

    # 初始URL
    start_urls = [
        'https://2.smzdm.com/',
       # 'https://2.smzdm.com/resources/js/main.1.0.js?v=2018042401'
    ]

    # 主域名
    main_domain = '2.smzdm.com'

    # 提取要下载的js与css资源, 并替换html
    def extract_resource(self, bs, response):
        resource_links = []

        link_tags = bs.select('script,link')
        for link_tag in link_tags:
            for attr in ['src', 'href']:
                if attr in link_tag.attrs:
                    link = response.urljoin(link_tag.attrs[attr])
                    link = link.strip()
                    link_tag.attrs[attr] = util.build_resource_path(self.main_domain, link) # 外链本地化路径
                    resource_links.append(link)  # 需要下载的js和css链接
        return self.filter_invalid_link(resource_links, ['.css', '.js'])

    # 提取<a>后链
    def extract_follow_link(self, bs, response):
        follow_links = []

        follow_tags = bs.select('a')
        for follow_tag in follow_tags:
            if 'href' in follow_tag.attrs:
                href = response.urljoin(follow_tag.attrs['href'])
                href = href.strip()
                url_info = urlparse(href)
                if url_info.netloc == self.main_domain:
                    follow_links.append(href)   # 只follow主域的后链
        return self.filter_invalid_link(follow_links)

    # 处理HTML, CSS, JS
    def parse(self, response):
        #print(response.url)
        if not self.filter_ext(response.url, ['.css', '.js']):
            bs = BeautifulSoup(response.body, 'lxml')

            # js, css资源
            resource_links = self.extract_resource(bs, response)
            for link in resource_links:
                #print("download:" + link)
                yield scrapy.Request(link, callback = self.parse, ) #dont_filter = True

            # a后链
            follow_links = self.extract_follow_link(bs, response)
            for link in follow_links:
                yield scrapy.Request(link, callback = self.parse, )

            item = items.XianzhiItem()
            item['url'] = response.url
            item['content'] = bs.prettify('utf-8') # 替换过链接的HTML页面
        else:
            item = items.XianzhiItem()
            item['url'] = response.url
            item['content'] = response.body # 原始的css和js

        yield item

    # 过滤后缀
    def filter_ext(self, link, ext):
        res = urlparse(link)
        if os.path.splitext(res.path)[-1] not in ext:
            return False
        return True

    # 无效链接过滤
    def filter_invalid_link(self, links, ext = None):
        def url_filter(url):
            res = urlparse(url)
            if res.scheme != 'http' and res.scheme != 'https':
                return False
            if ext is not None:
                if os.path.splitext(res.path)[-1] not in ext:
                    return False
            return True

        links = filter(url_filter, links)
        return list(links)

