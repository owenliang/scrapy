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
                    link_tag.attrs[attr] = util.build_resource_path(self.main_domain, link) # 外链本地化URL
                    resource_links.append(link)  # 需要下载的js和css链接
        return self.filter_invalid_link(resource_links, ['.css', '.js'])

    # 提取<a>后链
    def extract_follow_link(self, bs, response):
        follow_links = []

        follow_tags = bs.select('a')
        for follow_tag in follow_tags:
            if 'href' in follow_tag.attrs:
                link = response.urljoin(follow_tag.attrs['href'])
                link = link.strip()
                url_info = urlparse(link)
                if url_info.netloc == self.main_domain:
                    follow_tag.attrs['href'] = util.build_resource_path(self.main_domain, link)  # 链接本地化
                    follow_links.append(link)   # 只follow主域的后链
        return self.filter_invalid_link(follow_links)

    # 提取图片
    def extract_img_link(self, bs, response):
        img_links = []

        img_tags = bs.select('img')
        for img_tag in img_tags:
            if 'src' in img_tag.attrs:
                link = response.urljoin(img_tag.attrs['src'])
                link = link.strip()
                url_info = urlparse(link)
                if url_info.netloc == self.main_domain:
                    img_tag.attrs['src'] = util.build_resource_path(self.main_domain, link)  # 链接本地化
                    img_links.append(link)   # 只下载主站下的图片
        return self.filter_invalid_link(img_links)

    # 处理HTML, CSS, JS
    def parse(self, response):
        resp_type = response.meta['type'] if response.meta and 'type' in response.meta else 'normal'

        # 普通页面
        if resp_type == 'normal':
            bs = BeautifulSoup(response.body, 'lxml')

            # js, css资源
            resource_links = self.extract_resource(bs, response)
            for link in resource_links:
                yield scrapy.Request(link, callback = self.parse, meta = {'type': 'resource'})

            # a后链
            follow_links = self.extract_follow_link(bs, response)
            for link in follow_links:
                yield scrapy.Request(link, callback = self.parse, meta = {'type': 'normal'})

            # 图片
            img_links = self.extract_img_link(bs, response)
            for link in img_links:
                yield scrapy.Request(link, callback = self.parse, meta = {'type': 'img'})

            item = items.XianzhiItem()
            item['url'] = response.url
            item['content'] = bs.prettify('utf-8') # 替换过链接的HTML页面
        else:
            item = items.XianzhiItem()
            item['url'] = response.url
            item['content'] = response.body # 原始的css和js

        yield item

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

