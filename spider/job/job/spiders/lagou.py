# -*- coding: utf-8 -*-
import scrapy


class LagouspiderSpider(scrapy.Spider):
    name = 'lagouspider'
    allowed_domains = ['http://lagou.com']
    start_urls = ['http://http://lagou.com/']

    def parse(self, response):
        pass
