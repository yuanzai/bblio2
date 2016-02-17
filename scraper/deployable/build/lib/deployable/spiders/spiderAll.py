#python imports
import string
from datetime import datetime
import sys
import os
import re
sys.path.append('/home/ec2-user/bblio/')
sys.path.append('/home/ec2-user/bblio/build/')

#django imports
from search.models import Site, Document

#scrapy imports
#from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.spiders import CrawlSpider, Rule
from scrapy.selector import Selector
#from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.linkextractors.sgml import SgmlLinkExtractor
from scrapy import signals
from scrapy.xlib.pydispatch import dispatcher
import logging


#config import
import config_file

#ec2 import
import aws.ec2

class SpiderAll(CrawlSpider):
    name = "SpiderAll"
    rules = None
    groupName = None
    count = 0
    _restrict_xpath= ('//*[not(self::meta)]')
    id = None
    
    url_list = []

    ignored_extensions = [
    # images
    'mng', 'pct', 'bmp', 'gif', 'jpg', 'jpeg', 'png', 'pst', 'psp', 'tif',
    'tiff', 'ai', 'drw', 'dxf', 'eps', 'ps', 'svg',
    # audio
    'mp3', 'wma', 'ogg', 'wav', 'ra', 'aac', 'mid', 'au', 'aiff',
    # video
    '3gp', 'asf', 'asx', 'avi', 'mov', 'mp4', 'mpg', 'qt', 'rm', 'swf', 'wmv',
    'm4a',
    # office suites
    'xls', 'xlsx', 'ppt', 'pptx', 'doc', 'docx', 'odt', 'ods', 'odg', 'odp',
    # other
    'css', 'exe', 'bin', 'rss', 'zip', 'rar',
    ]


    def __init__(self, *a, **kw):
        self.follow = []
        self.parsing = []
        self.deny = []
        site = None
        if 'id' in kw:
            self.id = kw['id']

            site = Site.objects.get(pk=self.id)
            self.start_urls = site.source_start_urls.split(';')
            self.allowed_domains = site.source_allowed_domains.split(';')
            if site.parse_parameters:  self.parsing = site.parse_parameters.strip().encode('utf-8').split(";")
            if site.follow_parameters:  self.follow = site.follow_parameters.strip().encode('utf-8').split(";")   
            if site.deny_parameters: self.deny = site.deny_parameters.strip().encode('utf-8').split(";")    
        else:
            self.allowed_domains = kw['source_allowed_domains'].split(';')
            self.start_urls = kw['source_start_urls'].split(';')
            if kw['parse_parameters']: self.parsing = kw['parse_parameters'].strip().encode('utf-8').split(';')
            if kw['follow_parameters']: self.follow = kw['follow_parameters'].strip().encode('utf-8').split(';')
            if kw['deny_parameters']: self.deny = kw['deny_parameters'].strip().encode('utf-8').split(';')
        self.parsing = [i for i in self.parsing if i !='']
        self.follow = [i for i in self.follow if i !='']
        self.deny = [i for i in self.deny if i !='']
        
        config = config_file.get_config()
        universal_deny = config.get('bblio','universal_deny').strip().split(";")
        universal_deny = [i for i in universal_deny if i != '']
        self.deny.extend(universal_deny)
        if len(self.follow) > 0:
            for i,d in enumerate(self.follow):
                if "r'" in str(d[0:2]) and "'" in str(d[-1]):
                    self.follow[i] = d[2:-1]
        
        if len(self.parsing) > 0:
            for i,d in enumerate(self.parsing):
                if "r'" in str(d[0:2]) and "'" in str(d[-1]):
                    self.parsing[i] = d[2:-1]
        
        if len(self.deny) > 0:
            for i,d in enumerate(self.deny):
                if "r'" in str(d[0:2]) and "'" in str(d[-1]):
                    self.deny[i] = d[2:-1]
        if Document.objects.filter(site_id=self.id).count() > 0:
            self.url_list = Document.objects.filter(site_id=self.id).values_list('urlAddress')

        self.rules = (
                Rule(SgmlLinkExtractor(
                    allow=self.parsing,
                    deny=self.deny,
                    unique=True,
                    restrict_xpaths=self._restrict_xpath,
                    deny_extensions=self.ignored_extensions,
                    ), 
                    callback='parse_item', follow='true'),
                Rule(SgmlLinkExtractor(
                    allow=self.follow,
                    deny=self.deny,
                    unique=True,
                    restrict_xpaths=self._restrict_xpath,
                    ), 
                    callback='follow_item', follow='true'),
                )
        super(SpiderAll, self).__init__(*a, **kw) 
    
    def follow_item(self, response):
        logging.info('[%s] Following: %s' % (self.id, response.url))
        return None

    def parse_item(self, response):
        logging.info('[%s] Parsing Start: %s' % (self.id, response.url))
        #log.msg('response header' + response.headers['content-type'], level=log.INFO, spider=self)
        try:

            item = {
                    'urlAddress' : response.url,
                    'domain' :  self.allowed_domains,
                    'site' : Site.objects.get(pk=self.id),
                    'response_code' : response.status, 
                    'isUsed' : 0
                    }

            if '.pdf' in str(response.url[-4:]):
                pdf_name = str(self.id) + '_' + str(datetime.now().isoformat()) + '.pdf'
                path = '/home/ec2-user/bblio/scraper/pdf/'
                if not os.path.exists(path):
                    os.makedirs(path)
                item.update({
                        'document_html' : path + pdf_name,
                        'encoding' : 'PDF'
                        })
                logging.info('PDF path: ' + path + pdf_name)        
                
                with open(path + pdf_name, "wb") as f: 
                    f.write(response.body)
                f.close()
                #aws.ec2.copy_file_to_web_server(path+pdf_name ,path + pdf_name)
                aws.ec2.copy_file_to_S3(response.url, path + pdf_name)
                os.remove(path + pdf_name)
            else:
                item.update({
                    'encoding' : response.headers['content-type'].split('charset=')[-1],
                    'document_html': (response.body).decode('utf-8','ignore').encode('utf-8')
                    })

            if Document.objects.filter(site_id=self.id).filter(urlAddress=item['urlAddress']).count() == 1:
                logging.info('[%s] Parsing Doc Overwrite: %s' % (self.id, response.url))
                d = Document.objects.filter(site_id=self.id).filter(urlAddress=item['urlAddress'])[0]
                d.document_html = item['document_html']
                d.encoding = item['encoding']
                d.domain = item['domain']
                d.response_code = item['response_code']
                d.isUsed = 0
                d.save()
            else:
                d = Document(**item)
                d.save()
            
            logging.info('[%s] Parsing Success: %s' % (self.id, response.url))

            return
        except AttributeError:
            logging.info('* Cannot parse: ' + response.url)
            logging.info(sys.exc_info()[0])
            return

        except:
            logging.info('* Unexpected error:' + str(sys.exc_info()[0]) + '\n' + str(sys.exc_info()[1]))
            return

