# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import pymysql

class SpidersPipeline:
    # 测试 ip proxy
    # def process_item(self, item, spider):
    #     return item

    def process_item(self, item, spider):
        title = item['title']
        link = item['link']
        conn = pymysql.connect(host = '192.168.100.101',
                       port = 3306,
                       user = 'root',
                       password = 'rootroot',
                       database = 'douban',
                       charset = 'utf8mb4'
                        )
        try:
            with conn.cursor() as cursor:
                sql = "INSERT INTO `movie` (`name`, `url`) VALUES (%s, %s)"
                cursor.execute(sql, (title, link))
                conn.commit()
        except Exception as e:
            print(e)
        finally:
            conn.close()
        return item