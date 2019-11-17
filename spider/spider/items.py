# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
import re
from scrapy.loader import ItemLoader
from scrapy.loader.processors import MapCompose, TakeFirst, Identity, Join


class SpiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


class ArticleItemLoader(ItemLoader):
    default_output_processor = TakeFirst()


def data_convert(value):
    match_re = re.match(".*?(\d+.*)", value)
    if match_re:
        return match_re.group(1)
    else:
        return "1970-07-01"

    pass


"""
input_processor是在收集数据的过程中所做的处理，output_processor是数据yield之后进行的处理
"""

class JobboleArticleItem(scrapy.Item):
    title = scrapy.Field(
        # input_processor=MapCompose(add_jobbole, add_test),
        # output_processor=TakeFirst()
    )
    create_time = scrapy.Field(
        input_processor=MapCompose(data_convert)
    )
    url = scrapy.Field()
    url_object_id = scrapy.Field()
    front_image_url = scrapy.Field(
        output_processor=Identity()
    )
    front_image_path = scrapy.Field()
    #点赞数
    praise_nums = scrapy.Field()
    #评论数
    comment_nums = scrapy.Field()
    #查看数
    fav_nums = scrapy.Field()
    tags = scrapy.Field(
        output_processor=Join(separator=",")
    )
    content = scrapy.Field()

    pass