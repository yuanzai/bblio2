import sys
sys.path.append('/home/ec2-user/bblio/build/')
from sqlite3 import dbapi2 
from scrapy import log, signals
from search.models import Document, Site
import string
import MySQLdb
import pytz

class AllPipeline(object):
    def __init__(self):
        pass

    @classmethod
    def from_crawler(cls, crawler):
        pipeline = cls()
        crawler.signals.connect(pipeline.spider_opened, signals.spider_opened)
        crawler.signals.connect(pipeline.spider_closed, signals.spider_closed)
        return pipeline

    def spider_opened(self, spider):
        thisSite = Site.objects.get(pk=spider.id)
        thisSite.running = 1
        thisSite.save()
        #log.msg("Pipeline.spider_opened called", level=log.INFO)

    def spider_closed(self, spider):
        stats = spider.crawler.stats
        result = Site.objects.get(pk=spider.id)
        result.parseCount = stats.get_value('item_scraped_count')
        result.responseCount = stats.get_value('response_received_count')
        result.lastupdate = pytz.UTC.localize(stats.get_value('finish_time'))
        result.running = 0
        result.save()
        #log.msg("Pipeline.spider_closed called", level=log.DEBUG)
   
    def process_item(self, item, spider):
        
        log.msg("Pipeline.process_item", level=log.INFO)
        if item:
            item.save()
        return item
