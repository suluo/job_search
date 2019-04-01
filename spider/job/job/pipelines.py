# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import json
from pymongo import MongoClient
from scrapy.conf import settings
from datetime import datetime


class testJobPipeline(object):
    def process_item(self, item, spider):
        # print (type(item), item)
        return item


class JobMongoPipeline(object):
    def __init__(self):
        self.client = MongoClient(host=settings['MONGO_HOST'],
                                  port=settings['MONGO_PORT']).job

    def process_item(self, item, spider):
        postItem = dict(item)
        table = spider.name
        if spider.name == 'lagou' and isinstance(item, LagouCommentItem):
            table = "lagouComment"
        postItem['discovery_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(26, postItem)

        db = self.client[table]
        db.ensure_index("job_link")
        if db.find({"job_link": postItem['job_link']}).count() > 0:
            db.update({'job_link': postItem['job_link']}, postItem)
        else:
            db.insert(postItem)
        self.client[table].insert(postItem)
        return item


class MongoPipeline(object):
    def __init__(self, mongo_uri, mongo_db,mongo_user, mongo_password):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db
        self.mongo_user = mongo_user
        self.mongo_password = mongo_password

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=crawler.settings.get('MONGO_URI'),
            mongo_db=crawler.settings.get('MONGO_DATABASE', 'items'),
            mongo_user = crawler.settings.get('MONGO_USER'),
            mongo_password = crawler.settings.get('MONGO_PASSWORD'),
        )

    def open_spider(self, spider):
        self.client = MongoClient('mongodb://%s:%s@%s/admin' % (self.mongo_user,self.mongo_password,self.mongo_uri))
        self.db = self.client[self.mongo_db]

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
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
