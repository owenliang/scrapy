# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

from zspider import util
import os

class XianzhiPipeline(object):
    def process_item(self, item, spider):
        # 构建文件路径
        resource_path = util.build_resource_path('2.smzdm.com', item['url'])

        # 拼接到文件系统目录
        resource_path = spider.settings['XIANZHI_WEBROOT'] + resource_path

        # 创建目录
        os.makedirs(os.path.dirname(resource_path), exist_ok = True)

        # 保存到磁盘
        with open(resource_path, 'wb') as fp:
            fp.write(item['content'])

        return item
