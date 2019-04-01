# -*- coding: utf-8 -*-

from scrapy.selector import Selector
from scrapy_redis.spiders import RedisSpider
# from scrapy.spiders import CrawlSpider,Rule
# from scrapy.linkextractors import LinkExtractor
from scrapy.http import Request
from job.items import TencentItem


class TencentSpider(RedisSpider):
    name = "tencent"
    redis_key = "tencent:start_urls"
#    start_urls = [
#        'http://hr.tencent.com/position.php?&start=0#a'
#    ]

    def __init__(self, *args, **kwargs):
        domain = kwargs.pop('domain', '')
        self.allowed_domains = filter(None, domain.split(','))
        super(TencentSpider, self).__init__(*args, **kwargs)

    def parse(self, response):
        print ("24------", response)
        hxs = Selector(response)
        # sites = hxs.xpath('//*[@id="position"]/div[1]/table/tbody/tr[@class="even" or @class="odd"]')
        sites = hxs.xpath('//*[@id="position"]/div[1]/table/tr[@class="even"]|//*[@id="position"]/div[1]/table/tr[@class="odd"]')
        # print sites
        for site in sites:
            item = TencentItem()
            item['JobTitle'] = site.xpath('td[1]/a/text()').extract_first()
            item['DetailLink'] = 'http://hr.tencent.com/'+site.xpath('td[1]/a/@href').extract_first()
            # detailurl = 'http://hr.tencent.com/'+item['DetailLink'][0]
            item['JobType'] = site.xpath('td[2]/text()').extract_first()
            item['peoplenum'] = site.xpath('td[3]/text()').extract_first()
            item['location'] = site.xpath('td[4]/text()').extract_first()
            item['PostDate'] = site.xpath('td[5]/text()').extract_first()
            yield Request(url=item['DetailLink'], meta={'item': item}, callback=self.detail_parse)

        nexturl = 'http://hr.tencent.com/' + hxs.xpath('//*[@id="next"]/@href').extract_first()
        # print nexturl
        yield Request(url=nexturl, callback=self.parse)
        pass

    def detail_parse(self, response):
        item = response.meta['item']
        hxs = Selector(response)
        sites = hxs.xpath('//*[@id="position_detail"]/div/table')
        # print sites
        for site in sites:
            # item = TencentItem()
            item['peoplenum'] = site.xpath('tr[2]/td[3]/text()').re('\d+')
            item.setdefault('responsibilities', []).append(''.join(site.xpath('tr[3]/td/ul/li[position()>0]/text()').extract()))
            item.setdefault('requirements', []).append(''.join(site.xpath('tr[4]/td/ul/li[position()>0]/text()').extract()))
            # print (type(item), item)
            # print (type(meta), meta)
            yield item
        pass
