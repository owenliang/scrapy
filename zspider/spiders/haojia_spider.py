# -*- coding: utf-8 -*-

import scrapy
from .. import items
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from zspider import util
from .. import settings
from .. import items
import os
from urllib import parse
import json

# 好价api爬虫
class HaojiaSpider(scrapy.spiders.Spider):
    name = 'haojia'

    # 初始URL
    start_urls = [
       '',
    ]

    # 好价详情 -- 参数枚举
    haojia_detail_params = [{'name': 'f', 'value': ['iphone', 'android']}, {'name': 'v', 'value': [9.0, 9.1]}, {'name': 'weixin', 'value': [0, 1]}]

    # 构造函数
    def __init__(self, *args, **kwargs):
        super(HaojiaSpider, self).__init__(*args, **kwargs)

        # 生成所有的好价详情组合
        self.haojia_detail_enum = []
        util.build_enum(self.haojia_detail_params, self.haojia_detail_enum)

    # 第一个请求不做处理, 触发所有链接的爬取
    def parse(self, response):
        pass

    # 构造详情页请求
    def build_detail_request(self, article_id):
        # print('好价:', article['article_id'])
        for args in self.haojia_detail_enum:
            url = 'https://haojia-api.smzdm.com/v1/articles/' + article_id + '?' + parse.urlencode(args)
            yield scrapy.Request(url, callback=self.handle_haojia_detail, errback=self.handle_error, cookies={'device_id': '假的, 你服不服?'}, meta={'id': article_id, 'args': args})

    # 好价详情页处理
    def handle_haojia_detail(self, response):
        item = items.HaojiaDetailItem()
        item['id'] = response.meta['id']
        item['args'] = response.meta['args']
        item['content'] = response.body
        yield item

    # 错误处理
    def handle_error(self, failure):
        request = failure.request
        # pass