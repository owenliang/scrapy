# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy

# 闲置
class XianzhiItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    url = scrapy.Field()
    content = scrapy.Field()

# 好价列表页
class HomepageListItem(scrapy.Item):
    args = scrapy.Field()
    content = scrapy.Field()

# 好价详情页
class HaojiaDetailItem(scrapy.Item):
    args = scrapy.Field()
    content = scrapy.Field()
    id = scrapy.Field()