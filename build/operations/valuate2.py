import sys
sys.path.append('/home/ec2-user/bblio/build/')

import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'Build.settings'

import re
from scraper.scrapeController import link_extractor
from search.models import Site

for site in Site.objects.filter(grouping='').filter(id__gte=330):
    try:
        print site.id
        url = site.source_start_urls.split(';')
        links = link_extractor(url[0])
        if not links: continue
        for l in links:
            r_list = []
            r_list.append(re.compile('\d{4}/\d{2}/\d{2}/[^\s/]+'))
            r_list.append(re.compile('\d{4}/\d{2}/[^\s/]+'))

            if any([re.search(r, l['url']) for r in r_list]):
                print l['url']
                site.grouping = 'Auto YYYY MM string'
                site.save()
    except:
        pass

