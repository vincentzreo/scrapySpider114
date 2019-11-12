# -*- coding: utf-8 -*-
import scrapy
from scrapy import Selector
from scrapy import Request

from urllib import parse
import requests
import re
from ..items import JobboleArticleItem
from ..utils.common import get_md5
import json


class JobboleSpider(scrapy.Spider):
    name = 'jobbole'
    allowed_domains = ['news.cnblogs.com']
    start_urls = ['https://news.cnblogs.com/']

    def parse(self, response):
        """
        1.获取新闻列表页中的新闻url并交给scrapy进行下载后调用相应的解析方法
        2.获取下一页的url交给scrapy进行下载，下载完成后交给parse继续跟进
        """
        # url = response.xpath('//*[@id="entry_647141"]/div[2]/h2/a/@href').extract_first("")
        # url = response.xpath('//div[@id="news_list"]//h2[@class="news_entry"]/a/@href').extract()
        # url = response.xpath('//div[@id="news_list"]//h2[@class="news_entry"]/a/@href').extract_first()
        # urls = response.css('div#news_list h2 a::attr(href)').extract()

        post_nodes = response.css('div#news_list div.news_block')[7:8]
        for post_node in post_nodes:
            image_url = post_node.css('.entry_summary a img::attr(src)').extract_first("")
            post_url = post_node.css('h2 a::attr(href)').extract_first("")
            yield Request(url=parse.urljoin(response.url,post_url),meta={"front_image_url":image_url},callback=self.parse_detail)


        #提取下一页并交给scrapy进行处理
        # next_url = response.css('div.pager a:last-child::text').extract_first("")

        # next_url = response.xpath('//a[contains(text(),"Next >")]/@href').extract_first("")
        # next_url = response.css('div.pager a:last-child::attr(href)').extract_first("")
        # yield Request(url=parse.urljoin(response.url, next_url),callback=self.parse)

        # if next_url == "Next >":
        #     next_url = response.css('div.pager a:last-child::attr(href)').extract_first("")
        #     yield Request(url=parse.urljoin(response.url, next_url))
        pass

    def parse_detail(self, response):
        match_re = re.match(".*?(\d+)",response.url)
        if match_re:
            article_item = JobboleArticleItem()
            # title = response.css('#news_title a::text').extract_first("")
            title = response.xpath('//*[@id="news_title"]//a/text()').extract_first("")
            # create_time = response.css('#news_info .time::text').extract_first("")
            create_time = response.xpath('//*[@id="news_info"]//*[@class="time"]/text()').extract_first()
            match_re1 = re.match(".*?(\d+.*)",create_time)
            if match_re1:
                create_time = match_re1.group(1)
            # content = response.css('#news_content').extract()[0]
            content = response.xpath('//*[@id="news_content"]').extract()[0]
            # tag_list = response.css('.news_tags a::text').extract()
            tag_list = response.xpath('//*[@class="news_tags"]//a/text()').extract()
            tags = ','.join(tag_list)
            post_id = match_re.group(1)
            #第二个url如果之前不加/,则会添加到第一个url的子路径下，而非域名后
            # html = requests.get(url=parse.urljoin(response.url, "/NewsAjax/GetAjaxNewsInfo?contentId={}".format(post_id)))
            # j_data = json.loads(html.text)
            article_item["title"] = title
            article_item["create_time"] = create_time
            article_item["content"] = content
            article_item["tags"] = tags
            article_item["url"] = response.url
            if response.meta.get("front_image_url",""):
                article_item["front_image_url"] = [response.meta.get("front_image_url","")]
            else:
                article_item["front_image_url"] = []
            yield Request(url=parse.urljoin(response.url, "/NewsAjax/GetAjaxNewsInfo?contentId={}".format(post_id)),meta={"article_item":article_item}, callback=self.parse_nums)
            # praise_nums = j_data["DiggCount"]
            # fav_nums = j_data["TotalView"]
            # comment_nums = j_data["CommentCount"]
        pass

    def parse_nums(self,response):
        j_data = json.loads(response.text)
        article_item = response.meta.get("article_item","")

        praise_nums = j_data["DiggCount"]
        fav_nums = j_data["TotalView"]
        comment_nums = j_data["CommentCount"]

        article_item['praise_nums'] = praise_nums
        article_item['fav_nums'] = fav_nums
        article_item['comment_nums'] = comment_nums
        article_item['url_object_id'] = get_md5(article_item['url'])
        yield article_item
        pass
