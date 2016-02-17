# Scrapy settings for deployable project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#

BOT_NAME = 'deployable'

SPIDER_MODULES = ['deployable.spiders']
NEWSPIDER_MODULE = 'deployable.spiders'
ITEM_PIPELINES = {'deployable.pipelines.AllPipeline':1000}
DOWNLOAD_DELAY = 0.75
CONCURRENT_REQUESTS_PER_IP = 10

#ROBOTSTXT_OBEY = True

LOG_LEVEL = 'INFO'


import sys
sys.path.append('/home/ec2-user/bblio/build/')

import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'Build.settings'

# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'deployable (+http://www.yourdomain.com)'
