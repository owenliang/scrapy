# -*- coding: utf-8 -*-

import scrapy
from .. import items
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from zspider import util
from zspider.spiders.haojia_spider import HaojiaSpider
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

    # 首页列表参数枚举
    homepage_params = [{'name': 'f', 'value': ['iphone', 'android']}, {'name': 'v', 'value': [9.0, 9.1]}]

    # 构造函数
    def __init__(self, *args, **kwargs):
        super(HomepageSpider, self).__init__(*args, **kwargs)

        # 好价爬虫
        self.haojia_spider = HaojiaSpider()

        # 生成所有的首页列表组合
        self.homepage_enum = []
        util.build_enum(self.homepage_params, self.homepage_enum)

    # 第一个请求不做处理, 触发所有链接的爬取
    def parse(self, response):
        # 首页列表的前N页
        for page in range(0, settings.HOMEPAGE_PAGE_LIMIT + 1):
            # 参数组合
            for args in self.homepage_enum:
                args = args.copy()
                args['page'] = page
                url = 'https://homepage-api.smzdm.com/v1/home?' + parse.urlencode(args)
                yield scrapy.Request(url, callback = self.handle_list, errback = self.handle_error, cookies = {'device_id': '假的, 你服不服?'}, meta = args)

    # 列表页
    def handle_list(self, response):
        list_data = json.loads(response.body)
        if int(list_data['error_code']) != 0:
            return

        # 对好价文章发起抓取
        for article in list_data['data']['rows']:
            if int(article['article_channel_id']) in [1, 2, 3, 5, 21, 28]:
                yield from self.haojia_spider.build_detail_request(article['article_id'])

        # 产生列表Item
        item = items.HomepageListItem()
        item['args'] = response.meta
        item['content'] = response.body

        yield item

    # 好价详情
    def handle_haojia_detail(self, response):
        print(response.body)
        pass

    # 错误处理
    def handle_error(self, failure):
        request = failure.request
        # pass