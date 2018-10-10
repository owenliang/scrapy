# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

from zspider import util
from zspider.items import XianzhiItem
from zspider.items import HomepageListItem
from zspider.items import HaojiaDetailItem
from scrapy.exceptions import DropItem
import os

# 闲置
class XianzhiPipeline(object):
    def process_item(self, item, spider):
        # 判断不是属于自己的Item, 继续向后传递
        if not isinstance(item, XianzhiItem):
            return item

        # 构建文件路径
        resource_path = util.build_resource_path('2.smzdm.com', item['url'], True)

        # 拼接到文件系统目录
        resource_path = spider.settings['XIANZHI_WEBROOT'] + resource_path

        # 写入磁盘
        util.write_file(resource_path, item['content'])

        # 被成功处理
        raise DropItem()

# 首页列表页
class HomepageListPipeline(object):
    def process_item(self, item, spider):
        # 继续后传
        if not isinstance(item, HomepageListItem):
            return item

        # 写入磁盘
        save_path = spider.settings['HOMEPAGE_SAVE_PATH'] + '/{}/{}/{}/index.html'.format(item['args']['f'], item['args']['v'], item['args']['page'])

        util.write_file(save_path, item['content'])

        # 被成功处理
        raise DropItem()

# 好价详情页
class HaojiaDetailPipeline(object):
    def process_item(self, item, spider):
        # 继续后传
        if not isinstance(item, HaojiaDetailItem):
            return item

        # 写入磁盘
        save_path = spider.settings['HAOJIA_SAVE_PATH'] + '/{}/{}/{}/{}/index.html'.format(item['id'], item['args']['f'], item['args']['v'], item['args']['weixin'])

        util.write_file(save_path, item['content'])

        # 被成功处理
        raise DropItem()