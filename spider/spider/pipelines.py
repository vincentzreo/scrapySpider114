# -*- coding: utf-8 -*-
from scrapy.pipelines.images import ImagesPipeline
import codecs
import json
# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
'''
数据的保存都放在pipeline中
'''


class SpiderPipeline(object):
    def process_item(self, item, spider):
        return item


class JsonWithEncodingPipeline(object):
    # 自定义json文件的导出
    def __init__(self):
        # 打开文件
        #第二个参数设为w为覆盖,a为append
        self.file = codecs.open("article.json", "a", encoding="utf-8")

    # 固定的写法
    def process_item(self, item, spider):
        lines = json.dumps(dict(item), ensure_ascii=False) + "\n"
        self.file.write(lines)

        return item
    def spider_closed(self,spider):
        self.file.close()


class ImagePipeline(ImagesPipeline):
    def item_completed(self, results, item, info):
        if 'front_image_url' in item:
            for ok,value in results:
                image_file_path = value["path"]
            item['front_image_path'] = image_file_path
        return item
    pass
