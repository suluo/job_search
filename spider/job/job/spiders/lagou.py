# -*- coding: utf-8 -*-

from scrapy import Selector, FormRequest
from scrapy_redis.spiders import RedisSpider
# from scrapy.spiders import CrawlSpider,Rule
# from scrapy.linkextractors import LinkExtractor
from scrapy.http import Request
from job.items import LagouItem


class LagouSpider(RedisSpider):
    name = "lagou"
    redis_key = "lagou:start_urls"
    allow_domain = ['lagou.com']
    #start_urls = [
    #    "https://www.lagou.com/"
    #]
    login_url = "https://passport.lagou.com/login/login.html"

#    def __init__(self, *args, **kwargs):
#        domain = kwargs.pop('domain', '')
#        self.allowed_domains = filter(None, domain.split(','))
#        super(LagouSpider, self).__init__(*args, **kwargs)

    def login(self, response):
        # hxs = Selector(response)
        yield FormRequest.from_response(login_url,
                                        meta=response.meta,
                                        formda={'source': 'None',
                                                'redir': response.url,
                                                'form_email': 'sfenp_zero@163.com',
                                                'form_password': '123456789',
                                                'remember': 'on',
                                                'login': u'登录'},
                                        callback=self.parse)

    def parse(self, response):
        hxs = Selector(response)
        cates = hxs.xpath('//*[@class="menu_box"]')
        for cate in cates:
            item = LagouItem()
            item['category'] = cate.xpath('//div[@class="category-list"]/h2/text()').extract_first().strip()
            l1_cates = cate.xpath('//div[contains(@class,"menu_sub")]/dl')
            for l1_cate in l1_cates:
                item['l1_category'] = l1_cate.xpath("dt/span/text()").extract_first()
                for l2_cate in l1_cate.xpath("dd"):
                    item['l2_category'] = l2_cate.xpath('a/text()').extract_first()
                    cateUrl = l2_cate.xpath('a/@href').extract_first()
                    print (36, item, cateUrl)
                    # yield Request(url=cateUrl, meta={'item': item}, callback=self.cate_parse)
                    yield Request(url=cateUrl, meta={'item': item}, callback=self.cate_parse, dont_filter=True)

    def cate_parse(self, response):
        item = response.meta['item']
        hxs = Selector(response)
        sites = hxs.xpath('//div[@class="s_position_list"]/ul[@class="item_con_list"]/li')
        print (41, sites)
        for site in sites:
            item['job_id'] = site.xpath('@data-positionid').extract_first()
            # item['job_name'] = site.xpath('@data-positionname').extract_first()
            item['company_id'] = site.xpath('@data-companyid').extract_first()
            item['company_name'] = site.xpath('@data-companyname').extract_first()
            item['salary'] = site.xpath('@data-salary').extract_first()
            position = site.xpath('//div[@class="position"]')
            item['job_link'] = position.xpath('div[@class="p_top"]/a/@href').extract_first()
            item['fomat_time'] = position.xpath('//span[@class="format-time"]/text()').extract_first()
            # item['money'] = position.xpath('div[@class="p_bot"]/div/span/text()').extract_first()
            item['experience'] = position.xpath('div[@class="p_bot"]/div/text()').extract()
            company = site.xpath('//div[@class="company"]')
            item['company_link'] = company.xpath('div[@class="company_name"]/a/@href').extract_first()
            item['company_industry'] = company.xpath('div[@class="industry"]/text()').extract_first()
            item['com_logo_link'] = site.xpath('//div[@class="com_logo"]/a/@href').extract_first()
            # item['label'] = site.xpath('//div[@class="list_item_bot"]/div[1]/text()').extract()
            # item['advantage'] = site.xpath('//div[@class="list_item_bot"]/div[2]/text()').extract_first()

            print (61, item)
            yield Request(url=item['job_link'], meta={'item': item}, callback=self.detail_parse)
        next_page = hxs.xpath('//div[@class="pager_container"]/a[position()>3]/@href').extract()
        for next_url in next_page:
            print (64, response.meta['item'], item)
            yield Request(url=item['job_link'], meta={'item': response.meta['item']}, callback=self.cate_parse)
            # yield Request(url=item['job_link'], meta={'item': response.meta['item']}, callback=self.cate_parse, dont_filter=True)

    def detail_parse(self, response):
        item = response.meta['item']
        print (71, item)
        hxs = Selector(response)
        site = hxs.xpath('//div[@class="position-content"]')
        item['job_name'] = site.xpath('//div[@class="job_name"]/@title').extract_first()
        item['department'] = site.xpath('//div[@class="company"]/text()').extract_first()
        item['label'] = site.xpath('//div[@class="job_request"]//li[@class="labels"]/text()').extract()
        item['publish_time'] = site.xpath('//div[@class="job_request"]/p[@class="publish_time"]/text()').extract_first()

        site = hxs.xpath('//*[@id="job_detail"]')
        item['advantage'] = site.xpath('//*[@class="job-advantage"]/p/text()').extract_first()
        item['description'] = " ".join(site.xpath('//*[@class="job_bt"]/div/text()').extract())
        item['job_address'] = "".join(site.xpath('//*[contains(@class, "job-address")]/div[@class="work_addr"]/text()').extract())
        item['publish_name'] = site.xpath('//*[@class="jd_publisher"]//div[@class="publisher_name"]/a/@title').extract_first()
        item['publish_pos'] = site.xpath('//*[@class="jd_publisher"]//div[@class="publisher_name"]/span/text()').extract_first()

        site = hxs.xpath('//*[class="reviews-area"]/ul/li[1]/div[@class="review-right"]')
        item['review_stars'] = site.xpath('div[contains(@class, "review-starts")]//div[@class="starts"]/i[1]/@class').re("\d+")
        item['review_date'] = site.xpath('div[contains(@class, "review-starts")]/span/text()').extract_first()
        item['review_tags'] = site.xpath('div[contains(@class, "review-tags")]/div/text()').extract()
        item['review_content'] = site.xpath('div[@class="review-content"]/div/div/text()').extract_first()
        item['review_action'] = site.xpath('div[@class="review-action"]/a/span/text()').re("\d+")

        item['jobs_similar'] = hxs.xpath('//div[@id="jobs_similar"]//ul[contains(@class, "similar_list")]/li/@data-jobid').extract()
        print (92, item)
        yield item
        #yield Request(url=item['company_link'], callback=self.company_parse)
