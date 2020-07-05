# -*- coding: utf-8 -*-
import scrapy
from spiders.items import SpidersItem
from scrapy.selector import Selector
import pymysql

class MoviesSpider(scrapy.Spider):
    # 测试 ip proxy
    # name = 'movies'
    # allowed_domains = ['httpbin.org']
    # start_urls = ['http://httpbin.org/ip']

    # def parse(self, response):
    #     print(response.text)

    name = 'movies'
    allowed_domains = ['movie.douban.com']
    start_urls = ['https://movie.douban.com/top250']

    def start_requests(self):
            i=0
            url = f'https://movie.douban.com/top250?start={i*25}'
            yield scrapy.Request(url=url, callback=self.parse, dont_filter=False)

    def parse(self, response):
        # print(response.url)
        movies = Selector(response=response).xpath('//div[@class="hd"]')
        for movie in movies:
            titles = movie.xpath('./a/span/text()')
            links = movie.xpath('./a/@href')
            # 查看 mysql movie 表是否有数据
            # conn = pymysql.connect(host = '192.168.100.101',
            #            port = 3306,
            #            user = 'root',
            #            password = 'rootroot',
            #            database = 'douban',
            #            charset = 'utf8mb4'
            #             )
            # try:
            #     with conn.cursor() as cursor:
            #         count = cursor.execute('select * from movie;')
            #         print(f'查询到 {count} 条记录')
            #         result = cursor.fetchone()
            #         print(result)
            # finally:
            #     conn.close()
            title = titles.extract_first().strip()
            link = links.extract_first().strip()
            item = SpidersItem()
            item['title'] = title
            item['link'] = link
            yield item
