# -*- coding: utf-8 -*-

import scrapy
from .. import items
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from zspider import util
from .. import settings
import os
from urllib import parse
import json

# 首页api爬虫
class HomepageSpider(scrapy.spiders.Spider):
    name = 'homepage'

    # 初始URL
    start_urls = [
       'https://homepage-api.smzdm.com/v1/home',
    ]

    # 列表接口

    # 参数枚举
    args_enum = [{'name': 'f', 'value': ['iphone', 'android']}, {'name': 'v', 'value': [9.0, 9.1]}]

    # 第一个请求不做处理, 触发所有链接的爬取
    def parse(self, response):
        # 生成所有的参数组合
        args_enum = []
        util.build_enum(self.args_enum, args_enum)
        self.args_enum = args_enum

        # 循环翻页
        for page in range(0, settings.HOMEPAGE_PAGE_LIMIT):
            # 参数组合
            for args in self.args_enum:
                args = args.copy()
                args['page'] = page
                url = 'https://homepage-api.smzdm.com/v1/home?' + parse.urlencode(args)
                yield scrapy.Request(url, callback = self.handle_list, errback = self.handle_error, cookies = {'device_id': '假的, 你服不服?'}, meta = args)

    # 列表页
    def handle_list(self, response):
        list_data = json.loads(response.body)
        if int(list_data['error_code']) != 0:
            return

        # 产生列表Item
        item = items.HomepageListItem()
        item['args'] = response.meta
        item['content'] = response.body

        yield item

    # 错误处理
    def handle_error(self, failure):
        request = failure.request
        # pass