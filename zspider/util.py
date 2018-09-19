# -*- coding: utf-8 -*-

from urllib.parse import urlparse
import os

# 生成URL在磁盘上的保存路径
def build_resource_path(main_domain, url):
    url_info = urlparse(url)

    resource_path = []

    # 非本站域名, 放在子目录下
    if url_info.netloc != main_domain:
        domain_part = url_info.netloc
        resource_path.append(domain_part)

    # 去除path的左右/
    path_part = url_info.path.strip('/')

    # 检查是否有文件后缀, 没有则默认为index.html
    ext = os.path.splitext(path_part)[1]
    if not len(ext):
        path_part = path_part + '/index.html'

    path_part = path_part.strip('/')
    resource_path.append(path_part)

    # 连接
    resource_path = '/' + '/'. join(resource_path)

    # ?a=1&b=2部分
    if len(url_info.query):
        query_part = '_' + url_info.query
        resource_path = resource_path + query_part

    return resource_path

if __name__ == '__main__':
    path = build_resource_path('2.smzdm.com', 'https://3.smzdm.com/')
    print(path)