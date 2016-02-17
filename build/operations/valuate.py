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
            for i in range(10,20,1):
                r_list = []
                r_list.append(re.compile('page/' + str(i)))
                r_list.append(re.compile('Page/' + str(i)))
                r_list.append(re.compile('page=' + str(i)))
                r_list.append(re.compile('Page=' + str(i)))
                r_list.append(re.compile('p/' + str(i)))
                r_list.append(re.compile('P/' + str(i)))
                r_list.append(re.compile('p=' + str(i)))
                r_list.append(re.compile('P' + str(i)))

                if any([re.search(r, l['url']) for r in r_list]):
                    print l['url']
                    site.grouping = 'Auto Page -' + str(i)
                    site.save()
    except:
        pass

