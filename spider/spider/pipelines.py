# -*- coding: utf-8 -*-
from scrapy.pipelines.images import ImagesPipeline
import codecs
import json
from scrapy.exporters import JsonItemExporter
from twisted.enterprise import adbapi
import MySQLdb
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


class MysqlPipeline(object):
    def __init__(self):
        self.conn = MySQLdb.connect("127.0.0.1", "root", "root", "article_spider", charset="utf8", use_unicode=True)
        self.cursor = self.conn.cursor()

    # 固定的写法
    def process_item(self, item, spider):
        insert_sql = """
            insert into jobbole_article(title, url, url_object_id, front_image_url, front_image_path, 
            praise_nums, comment_nums, fav_nums, tags, content, create_data)
            values (%s, %s, %s, %s, %s,%s, %s, %s, %s, %s, %s)
        """
        params = []
        params.append(item.get("title", ""))
        params.append(item.get("url", ""))
        params.append(item.get("url_object_id", ""))
        front_image = ",".join(item.get("front_image_url",[]))
        params.append(item.get("front_image_url", front_image))
        params.append(item.get("front_image_path", ""))
        params.append(item.get("praise_nums", 0))
        params.append(item.get("comment_nums", 0))
        params.append(item.get("fav_nums", 0))
        params.append(item.get("tags", ""))
        params.append(item.get("content", ""))
        params.append(item.get("create_data", "1970-07-01"))
        self.cursor.execute(insert_sql, tuple(params))
        self.conn.commit()

        return item

    def spider_closed(self,spider):
        pass


class MysqlTwistedPipeline(object):
    def __init__(self, dbpool):
        self.dbpool = dbpool
        pass

    @classmethod
    def from_settings(cls, settings):
        from MySQLdb.cursors import DictCursor
        dbparms = dict(
            host=settings["MYSQL_HOST"],
            db=settings["MYSQL_DBNAME"],
            user=settings["MYSQL_USER"],
            password=settings["MYSQL_PASSWORD"],
            charset='utf8',
            cursorclass=DictCursor,
            use_unicode=True
        )
        dbpool = adbapi.ConnectionPool("MySQLdb", **dbparms)
        return cls(dbpool)
        pass

    def process_item(self, item, spider):
        query = self.dbpool.runInteraction(self.do_insert,item)
        query.addErrback(self.handle_error, item, spider)
        pass

    def handle_error(self, failure, item, spider):
        print(failure)
        pass

    def do_insert(self, cursor, item):
        insert_sql = """
                    insert into jobbole_article(title, url, url_object_id, front_image_url, front_image_path, 
                    praise_nums, comment_nums, fav_nums, tags, content, create_data)
                    values (%s, %s, %s, %s, %s,%s, %s, %s, %s, %s, %s) ON DUPLICATE KEY UPDATE praise_nums=VALUES(praise_nums)
                """
        params = []
        params.append(item.get("title", ""))
        params.append(item.get("url", ""))
        params.append(item.get("url_object_id", ""))
        front_image = ",".join(item.get("front_image_url", []))
        params.append(item.get("front_image_url", front_image))
        params.append(item.get("front_image_path", ""))
        params.append(item.get("praise_nums", 0))
        params.append(item.get("comment_nums", 0))
        params.append(item.get("fav_nums", 0))
        params.append(item.get("tags", ""))
        params.append(item.get("content", ""))
        params.append(item.get("create_time", "1970-07-01"))


        cursor.execute(insert_sql, tuple(params))

        pass


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


class JsonExporterPipeline(object):
    def __init__(self):
        # 打开文件
        self.file = open('articleexport.json', 'wb')
        self.exporter = JsonItemExporter(self.file, encoding="utf-8", ensure_ascii=False)
        self.exporter.start_exporting()

    # 固定的写法
    def process_item(self, item, spider):
        self.exporter.export_item(item)

        return item
    def spider_closed(self,spider):
        self.exporter.finish_exporting()
        self.file.close()


class ImagePipeline(ImagesPipeline):
    def item_completed(self, results, item, info):
        if 'front_image_url' in item:
            image_file_path = ""
            for ok,value in results:
                image_file_path = value["path"]
            item['front_image_path'] = image_file_path
        return item
    pass

