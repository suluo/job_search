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
    # Tencent
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


class LagouItem(Item):
    job_id = Field()
    job_name = Field()
    category = Field()
    l1_category = Field()
    l2_category = Field()
    salary = Field()
    job_link = Field()
    format_time = Field()
    experience = Field()

    company_id = Field()
    company_name = Field()
    company_link = Field()
    company_industry = Field()
    com_logo_link = Field()

    label = Field()
    advantage = Field()
    department = Field()
    publish_time = Field()
    description = Field()
    job_address = Field()
    publish_name = Field()
    publish_pos = Field()

    review_stars = Field()
    review_date = Field()
    review_tags = Field()
    review_content = Field()
    review_action = Field()

    jobs_similar = Field()


class LagouCommentItem(Item):
    pass
