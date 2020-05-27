# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import pymysql

import datetime


class NewsPipeline(object):
    def __init__(self, mysql_options):
        self.conn = pymysql.connect(**mysql_options)

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mysql_options=crawler.settings.get('MY_MYSQL')
        )

    def open_spider(self, spider):
        self.cursor = self.conn.cursor()

    def close_spider(self, spider):
        self.cursor.close()
        self.conn.close()

    def process_item(self, item, spider):
        item['publish_date'] = datetime.datetime.strptime(item['publish_date'], '%Y-%m-%d %H:%M:%S') - datetime.timedelta(hours=8)
        sql = "insert into news(`category`, `title`, `media`, `created_at`, `content`, `url`) value('{}','{}','{}','{}','{}','{}')".format(
            item['category'],
            item['title'],
            item['media'],
            item['publish_date'],
            item['content'],
            item['url'],
        )
        try:
            self.cursor.execute(sql)
            self.conn.commit()
            spider.logger.info('detail-save {} 写入成功'.format(item['title']))
        except Exception as e:
            self.conn.rollback()
            spider.logger.info('detail-save {} 写入失败 {}'.format(item['title'], str(e)))

        return item


