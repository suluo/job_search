# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy import Item, Field


class JobItem(Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


class TencentItem(Item):
    JobTitle = Field()
    DetailLink = Field()
    JobType = Field()
    peoplenum = Field()
    location = Field()
    PostDate = Field()
    peoplenum = Field()
    responsibilities = Field()
    requirements = Field()
    pass


class LagouCommentItem(Item):
    pass
