# -*- coding: utf-8 -*-
import scrapy
from ..items import NewsItem
from bs4 import BeautifulSoup, Comment
import re
from scrapy.http.response import Response
import datetime

class NewsSpider(scrapy.Spider):
    name = 'news'
    allowed_domains = ['10jqka.com.cn']
    start_page = 2
    start_urls = [
        'http://news.10jqka.com.cn/today_list/index_2.shtml',
        'http://news.10jqka.com.cn/cjzx_list/index_2.shtml',
        'http://news.10jqka.com.cn/cjkx_list/index_2.shtml',
        'http://news.10jqka.com.cn/guojicj_list/index_2.shtml',
        'http://news.10jqka.com.cn/jrsc_list/index_2.shtml',
        'http://news.10jqka.com.cn/fssgsxw_list/index_2.shtml',
        'http://news.10jqka.com.cn/region_list/index_2.shtml',
        'http://news.10jqka.com.cn/fortune_list/index_2.shtml',
        'http://news.10jqka.com.cn/cjrw_list/index_2.shtml',
    ]

    # def start_requests(self):
    #     href = 'http://news.10jqka.com.cn/20200323/c618718185.shtml'
    #     yield scrapy.Request(href, callback=self.parse_html)

    def check_detail_url(self, url):
        if url.find(self.allowed_domains[0]) != -1:
            preg = re.search(r'/(?P<y>20\d{2})(?P<m>[0-1]\d)(?P<d>[0-3]\d)/', url)
            if preg:
                compile_str = '{}{}{}'.format(preg.group('y'), preg.group('m'), preg.group('d'))
                cur_stamp = int(datetime.datetime.today().timestamp())
                compile_stamp = int(datetime.datetime.strptime(compile_str, '%Y%m%d').timestamp())
                if compile_stamp > cur_stamp - 86400 * 3:
                    return True
        return False

    def parse(self, response):
        node_curpage = response.xpath('//span[@class="num-container"]/a[@class="num"]/text()')
        if node_curpage:
            cur_page = int(node_curpage.extract_first())
        else:
            cur_page = 0
            print('找不到当前页码')

        # 获取上一页
        pre_page = response.xpath('//div[@class="bottom-page"]//a[@class="prev"]/@href').extract_first()
        if pre_page != None:
            print(cur_page, pre_page)
            yield scrapy.Request(pre_page.strip(), callback=self.parse, dont_filter=True)

        # 处理列表
        try:
            category = response.xpath('//span[@class="pagecrumbs"]/a/text()').extract()[-1]
            # 倒序处理
            for node in reversed(response.xpath('//div[@class="list-con"]//li')):
                href = node.xpath('./span/a//@href').extract_first()
                title = node.xpath('./span/a//@title').extract_first()
                dt = node.xpath('./span/span/text()').extract_first()
                if self.check_detail_url(href):
                    self.logger.info('list[{}]-[{}][{}][{}][{}]'.format(cur_page, category, title, dt, href))
                    yield scrapy.Request(href, callback=self.parse_html, dont_filter=False)
        except Exception as e:
            print('list', e)

    def parse_html(self, response: Response):
        if self.check_detail_url(response.url):
            try:
                # bs4 + 正则
                html_body = response.text  # .replace('<p', '<pdiv').replace('</p>', '</pdiv>')
                soup = BeautifulSoup(html_body, 'lxml')
                category = soup.find(attrs={'class': "top-channel"}).contents[-2].string
                title = soup.find('h2', attrs={'class': 'main-title'}).string
                dt = soup.find('span', attrs={'id': 'pubtime_baidu'}).string

                # 处理来源
                media = ''
                media_node = soup.find(text=re.compile('来源：')).next_sibling.string
                if media_node:
                    media = media_node.strip()

                # 处理内容
                con = soup.find('div', attrs={'class': 'main-text atc-content'})

                # 去除行情图
                [x.extract() for x in con.findAll(attrs={'class': 'acthq'})]
                # 去除注释
                [comment.extract() for comment in con.findAll(text=lambda text: isinstance(text, Comment))]
                [x.extract() for x in con.findAll(attrs={'class': re.compile('(bottomSign|editor)')})]
                [x.extract() for x in con.findAll('script')]
                [x.extract() for x in con.findAll(id='arctTailMark')]
                # [x.extract() for x in con.findAll(text='\n')]
                [x.parent.extract() for x in con.findAll(text=re.compile('同花顺上线「疫情地图」'))]
                # 正则替换a标签
                content = ''.join(map(str, con.contents))
                content = re.sub(r'<a([^>]*?)>(?P<a_text>.*?)</a>', '\g<a_text>', content)
                content = re.sub(r'<img([^>]*?)src="(?P<imgsrc>[^">]*?)"([^>]*?)>', '<img src="\g<imgsrc>" />', content)
                content = re.sub('\r|\n|\r\n|\u3000|<p></p>| class="" contenteditable="false"', '', content)
                # content = content.replace("\u3000", '  ').replace("\n", '').replace("\r", '').replace("\r\n", '').replace('<p></p>', '')

                item = NewsItem()
                item['category'] = category
                item['title'] = title
                item['media'] = media
                item['publish_date'] = dt
                item['content'] = content
                item['url'] = response.url
                self.logger.info('detail-parse-[{}]url正常'.format(response.url))

                yield item
            except Exception as e:
                self.logger.info('detail-parse-[{}]parse异常'.format(response.url))
        else:
            self.logger.info('detail-parse-[{}]url异常'.format(response.url))
