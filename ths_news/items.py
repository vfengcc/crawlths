# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class NewsItem(scrapy.Item):
    category = scrapy.Field()       # 分类
    title = scrapy.Field()          # 标题
    media = scrapy.Field()          # 来源
    content = scrapy.Field()        # 内容
    publish_date = scrapy.Field()     # 发布时间
    url = scrapy.Field()

