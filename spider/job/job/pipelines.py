# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import json
from pymongo import MongoClient
from scrapy.conf import settings


class testJobPipeline(object):
    def process_item(self, item, spider):
        # print (type(item), item)
        return item


class JobMongoPipeline(object):
    def __init__(self):
        self.client = MongoClient(host=settings['MONGO_HOST'],
                                  port=settings['MONGO_PORT']).job

    def process_item(self, item, spider):
        if spider.name == 'lagou' and isinstance(item, LagouCommentItem):
            postItem = dict(item)
            self.client.lagoucomment.insert(postItem)
        else:
            postItem = dict(item)
            self.client[spider.name].insert(postItem)
        return item


class JsonWritePipeline(object):
    def __init__(self):
        self.file = open('filename.json', 'w', encoding='utf-8')

    def process_item(self, item, spider):
        line = json.dumps(dict(item), ensure_ascii=False)
        self.file.write(line + "\n")
        return item

    def spider_closed(self, spider):
        self.file.close()
