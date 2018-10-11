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
import sys

# 好价api爬虫
class HaojiaSpider(scrapy.spiders.Spider):
    name = 'haojia'

    # 初始URL
    start_urls = [
       'https://haojia-api.smzdm.com/v1/articles/',
    ]

    # 好价列表 -- 参数枚举
    haojia_list_params = [{'name': 'f', 'value': ['iphone', 'android']}, {'name': 'v', 'value': [9.0, 9.1]},]

    # 好价详情 -- 参数枚举
    haojia_detail_params = [{'name': 'f', 'value': ['iphone', 'android']}, {'name': 'v', 'value': [9.0, 9.1]}, {'name': 'weixin', 'value': [0, 1]}]

    # 构造函数
    def __init__(self, *args, **kwargs):
        super(HaojiaSpider, self).__init__(*args, **kwargs)

        # 生成所有的好价详情组合
        self.haojia_detail_enum = []
        util.build_enum(self.haojia_detail_params, self.haojia_detail_enum)

        # 生成所有好价列表组合
        self.haojia_list_enum = []
        util.build_enum(self.haojia_list_params, self.haojia_list_enum)

    # 第一个请求不做处理, 触发所有链接的爬取
    def parse(self, response):
        # 好价列表的前N页
        for page in range(1, settings.HAOJIA_PAGE_LIMIT + 1):
            # 参数组合
            for args in self.haojia_list_enum:
                args = args.copy()
                args['page'] = page
                args['z_debug'] = 'TH9bQXpIuYV0'
                url = 'https://haojia-api.smzdm.com/v1/home/list?' + parse.urlencode(args)
                yield scrapy.Request(url, callback=self.handle_list, errback=self.handle_error,
                                     cookies={'device_id': '假的, 你服不服?'}, meta=args)

    # 构造详情页请求
    def build_detail_request(self, article_id, options = None):
        # print('好价:', article['article_id'])
        for args in self.haojia_detail_enum:
            args = args.copy()
            args['z_debug'] = 'TH9bQXpIuYV0'
            if options is not None:
                args.update(options)
            url = 'https://haojia-api.smzdm.com/v1/articles/' + article_id + '?' + parse.urlencode(args)
            yield scrapy.Request(url, callback=self.handle_haojia_detail, errback=self.handle_error, cookies={'device_id': '假的, 你服不服?'}, meta={'id': article_id, 'args': args})

    # 好价详情页处理
    def handle_haojia_detail(self, response):
        item = items.HaojiaDetailItem()
        item['id'] = response.meta['id']
        item['args'] = response.meta['args']
        item['content'] = response.body
        yield item

    # 列表页
    def handle_list(self, response):
        list_data = json.loads(response.body)
        if int(list_data['error_code']) != 0:
            return

        # 对好价文章发起抓取
        for article in list_data['data']['rows']:
            # 普通格式
            if 'article_id' in article:
                yield from self.build_detail_request(article['article_id'], {'channel_id': article['article_channel_id']})
            # 横栏模式
            if 'article_rows' in article:
                for sub_article in article['article_rows']:
                    yield from self.build_detail_request(sub_article['article_id'], {'channel_id': sub_article['article_channel_id']})

        # 产生列表Item
        item = items.HaojiaListItem()
        item['args'] = response.meta
        item['content'] = response.body
        yield item

    # 错误处理
    def handle_error(self, failure):
        request = failure.request
        # pass