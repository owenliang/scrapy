# -*- coding: utf-8 -*-

from urllib.parse import urlparse
import os

# 生成URL在磁盘上的保存路径
def build_resource_path(main_domain, url, disk = False):
    url_info = urlparse(url)

    parts = []

    # 1, 域名处理: 主站域名不出现在路径中
    if url_info.netloc != main_domain:
        parts.append(url_info.netloc)

    # 2, 文件后缀
    uri = url_info.path.strip('/')
    if disk:
        ext = os.path.splitext(uri)[1]
        if not len(ext):
            if len(uri):
                uri = uri + '/index.html'
            else:
                uri = 'index.html'
    parts.append(uri)

    # 3, 连接domain与uri
    resource_path = '/' + '/'. join(parts)

    # 4, 非disk路径保留query string
    if not disk and len(url_info.query):
        resource_path = resource_path + '?' + url_info.query

    return resource_path

# 生成所有参数枚举
def build_enum(kvs, all_enum, start = 0, cur_enum = None):
    if cur_enum is None:
        cur_enum = {}

    if len(cur_enum) == len(kvs):
        all_enum.append(cur_enum.copy())
        return

    kv = kvs[start]
    k = kv['name']
    v_arr = kv['value']
    for v in v_arr:
        cur_enum[k] = v
        build_enum(kvs, all_enum, start + 1, cur_enum)
        del cur_enum[k]


# 写文件
def write_file(filename, content):
    # 创建目录
    os.makedirs(os.path.dirname(filename), exist_ok=True)

    # 保存到磁盘
    with open(filename, 'wb') as fp:
        fp.write(content)

if __name__ == '__main__':
    #path = build_resource_path('2.smzdm.com', 'https://2.smzdm.com/a/b?a=1', True)
    #print(path)

    kvs = [{'name': 'f', 'value': ['iphone', 'android']}, {'name': 'v', 'value': [9.0, 9.1]}]
    ret = []
    build_enum(kvs, ret)
    print(ret)
