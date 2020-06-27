import scrapy
from scrapy.selector import Selector

from maoyan.items import MaoyanItem


class MaoyanmovieSpider(scrapy.Spider):
    name = 'maoyanmovie'
    allowed_domains = ['maoyan.com']
    start_urls = ['http://maoyan.com/films?showType=3']

    def parse(self, response):
        movies = Selector(response=response).xpath('//div[@class="movie-hover-info"]')
        # 取前 10 电影，初始化计数器
        count = 10

        for movie in movies:
            if count > 0:
                count -= 1
                title = movie.xpath('.//span[contains(@class,"name")]/text()').extract_first()
                hover_tags = movie.xpath('.//span[contains(@class,"hover-tag")]/../text()')
                types = (hover_tags.extract())[1].strip()
                dates = (hover_tags.extract())[5].strip()

                item = MaoyanItem()
                item['title'] = title
                item['types'] = types
                item['dates'] = dates
                yield item
