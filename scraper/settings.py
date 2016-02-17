#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#

BOT_NAME = 'scrapeAll'

SPIDER_MODULES = ['spiders']
NEWSPIDER_MODULE = 'spiders'
ITEM_PIPELINES = {'pipelines.AllPipeline':1000}
DOWNLOAD_DELAY = .75
DEPTH_LIMIT = 0
MEMUSAGE_ENABLED = True
MEMUSAGE_REPORT = True
MEMDEBUG_ENABLED = True
MEMUSUAGE_LIMIT_MB = 150
MEMUSAGE_NOTIFY_MAIL = ['junyuan.lau@gmail.com']
CONCURRENT_ITEMS = 40
CONCURRENT_REQUESTS = 10
CONCURRENT_REQUESTS_PER_DOMAIN = 1

JOBDIR = '/home/ec2-user/bblio/scraper/crawls/'
LOG_LEVEL = 'INFO'
LOG_ENABLED = False

import sys
sys.path.append('/home/ec2-user/bblio/')

import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'build.Build.settings'

# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'tutorial (+http://www.yourdomain.com)'
