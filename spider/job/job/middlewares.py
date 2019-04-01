# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/spider-middleware.html
from scrapy import signals
from pymongo import MongoClient
from scrapy.conf import settings
from fake_useragent import UserAgent
import requests
import logging
import random
import time


class JobSpiderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, dict or Item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Response, dict
        # or Item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class JobMongoProxyMiddleware(object):
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.client = MongoClient(host=settings['MONGO_HOST'],
                                  port=settings['MONGO_PORT']).ip

    def process_request(self, request, spider):
        '''对request对象加上proxy'''
        proxy = self.get_random_proxy(spider.name)
        time.sleep(1)
        if proxy is not None:
            request.meta['proxy'] = proxy
        else:
            request.meta['proxy'] = "https://101.236.53.143:8080"
            print("The request proxy is None")
        print("79, this is request ip:" + request.meta['proxy'])

    def process_response(self, request, response, spider):
        '''对返回的response处理'''
        # 如果返回的response状态不是200，重新生成当前request对象
        if response.status != 200:
            proxy = self.get_random_proxy(spider.name)
            # 对当前reque加上代理
            if proxy is not None:
                request.meta['proxy'] = proxy
            else:
                request.meta['proxy'] = "https://101.236.53.143:8080"
                print("The response proxy is None")
            print("this is response ip:" + request.meta['proxy'])
            return request
        time.sleep(1)
        return response

#    def process_exception(self, request, exception, spider):
#        # self.logger.info("Get Exception")
#        request.meta['request'] = "http://127.0.0.1:9743"
#        print("this is exception ip:" + request.meta['request'])
#        return request

    def get_random_proxy(self, spidername):
        '''随机读取proxy'''
        # print ("tables is", self.client.collection_names())
        for table in ['xici']:
            query = {
                "ip": {"$exists": True},
                'http': {"$in": ['http', 'https', 'HTTP', 'HTTPS']},
                "anonymity": "高匿",
            }
            print(110, table, query)
            items = self.client[table].find(query)
            if items.count() < 1:
                continue
            rint = random.randint(0, items.count()-1)
            itemiter = items.limit(0).skip(rint)
            # 随机选取
            for i in range(10):
            # while True:
                try:
                    ip = next(itemiter)
                    ip['ip_port'] = ip['ip']
                    if self.check_valid_ip(spidername, ip):
                        proxy = ip["http"].lower() + "://" + ip['ip_port']
                        return proxy
                    time.sleep(5)
                except Exception:
                    self.logger.error("error", exc_info=True)
                    break
        else:
            return None

    def check_valid_ip(self, spidername, ip):
        url_map = {
            "lagou": "https://www.lagou.com",
            "other": "https://music.163.com"
        }
        ua = UserAgent(verify_ssl=False)
        headers = {'User-Agent': ua.random, "Connection": "close"}
        proxies = {ip['http'].lower(): ip['http'].lower() + "://" + ip['ip_port']}
        url = url_map.get(spidername, url_map['other'])
        try:
            requests.adapters.DEFAULT_RETRIES = 3
            res = requests.get(url=url, proxies=proxies,
                               headers=headers, timeout=60)
            print (135, proxies, res.headers)
            if str(res.status_code).startswith("20"):
                return True
            else:
                res.raise_for_status()  # 如果响应状态码不是200,主动抛出异常
        except Exception:
            logging.error("error", exc_info=True)
            print (proxies, "is not valid")
            # self.client[table].remove({"http": ip['http'], 'ip_port': ip['ip_port']})
            return False


class JobProxyMiddleware(object):
    def __init__(self):
        self.IPPOOL = [
            "https://127.0.0.1:8087"
        ]

    def process_request(self, request, spider):
        '''对request对象加上proxy'''
        proxy = random.choice(self.IPPOOL)
        print("this is request ip:" + proxy)
        time.sleep(1)
        request.meta['proxy'] = proxy

    def process_response(self, request, response, spider):
        '''对返回的response处理'''
        # 如果返回的response状态不是200，重新生成当前request对象
        if response.status != 200:
            proxy = random.choice(self.IPPOOL)
            print("this is response ip:" + proxy)
            # 对当前reque加上代理
            request.meta['proxy'] = proxy
            return request
        time.sleep(1)
        return response


class RandomUserAgentMiddleWare(object):
    """
    随机更换User-Agent
    """
    def __init__(self, crawler):
        super(RandomUserAgentMiddleWare, self).__init__()
        self.ua = UserAgent(verify_ssl=False)
        self.ua_type = crawler.settings.get("RANDOM_UA_TYPE", "random")

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler)

    def process_request(self, request, spider):
        def get_ua_type():
            # 取对象 ua 的 ua_type 的这个属性, 相当于 self.ua.self.ua_type
            return getattr(self.ua, self.ua_type)

        # random_useragent = get_ua_type()
        request.headers['User-Agent'] = get_ua_type()
        # print (165, 'middleware', self.ua_type, request.headers)

    def _get_agent(self, ):
        UserAgent_List = [
                "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.1 Safari/537.36",
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.0 Safari/537.36",
                "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.0 Safari/537.36",
                "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2226.0 Safari/537.36",
                "Mozilla/5.0 (Windows NT 6.4; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2225.0 Safari/537.36",
                "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2225.0 Safari/537.36",
                "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2224.3 Safari/537.36",
                "Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/40.0.2214.93 Safari/537.36",
                "Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/40.0.2214.93 Safari/537.36",
                "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2049.0 Safari/537.36",
                "Mozilla/5.0 (Windows NT 4.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2049.0 Safari/537.36",
                "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.67 Safari/537.36",
                "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.67 Safari/537.36",
                "Mozilla/5.0 (X11; OpenBSD i386) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1944.0 Safari/537.36",
                "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.3319.102 Safari/537.36",
                "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.2309.372 Safari/537.36",
                "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.2117.157 Safari/537.36",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36",
                "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1866.237 Safari/537.36",
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.137 Safari/4E423F",
                "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0) Gecko/20100101 Firefox/40.1",
                "Mozilla/5.0 (Windows NT 6.3; rv:36.0) Gecko/20100101 Firefox/36.0",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10; rv:33.0) Gecko/20100101 Firefox/33.0",
                "Mozilla/5.0 (X11; Linux i586; rv:31.0) Gecko/20100101 Firefox/31.0",
                "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:31.0) Gecko/20130401 Firefox/31.0",
                "Mozilla/5.0 (Windows NT 5.1; rv:31.0) Gecko/20100101 Firefox/31.0",
                "Opera/9.80 (X11; Linux i686; Ubuntu/14.10) Presto/2.12.388 Version/12.16",
                "Opera/9.80 (Windows NT 6.0) Presto/2.12.388 Version/12.14",
                "Mozilla/5.0 (Windows NT 6.0; rv:2.0) Gecko/20100101 Firefox/4.0 Opera 12.14",
                "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.0) Opera 12.14",
                "Opera/9.80 (Windows NT 5.1; U; zh-sg) Presto/2.9.181 Version/12.00"
        ]
        return random.choice(UserAgent_List)

