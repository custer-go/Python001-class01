# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter


class MaoyanPipeline:
    def process_item(self, item, spider):
        title = item['title']
        types = item['types']
        dates = item['dates']
        output = f'|{title}|\t|{types}|\t|{dates}|\n\n'
        with open('./movie.txt', 'a+', encoding='utf-8') as article:
            article.write(output)
        return item
