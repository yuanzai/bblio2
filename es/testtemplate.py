import sys
sys.path.append('/home/ec2-user/bblio/build/')

import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'Build.settings'

from django.db import connection
from search.models import Site, Document, TextFilter
from TemplateTerms import TemplateTerms
from YTHESController import YTHESController as ESController

this_site = 2

def headfoot(site_id):
    es = ESController()
    docs = [' '.join(es.text_array(d)).encode('utf-8')  for d in Document.objects.filter(site_id=site_id).exclude(encoding='PDF')]
    print len(docs)

    tt = TemplateTerms(docs)
    tt.generate(1)
    """ 
    for key, value in tt._max_group['grouping'].iteritems():
        print key
    print '---------------------------'
    for key, value in tt._max_group_reverse['grouping'].iteritems():
        print key
    """
    if tt._max_group:
        print 'head: ' + tt._max_group['grouping'].iterkeys().next()
        tf = None
        if TextFilter.objects.filter(filter_id=1).filter(filter_type='head').filter(site_id=site_id).count() == 1:
            tf = TextFilter.objects.filter(filter_id=1).filter(filter_type='head').filter(site_id=site_id)[0]
        else:
            tf = TextFilter()

        tf.filter_id = 1
        tf.filter_text = tt._max_group['grouping'].iterkeys().next()
        tf.filter_type = 'head'
        tf.site_id = site_id
        tf.save()

    if tt._max_group_reverse:
        print 'foot: ' +  tt._max_group_reverse['grouping'].iterkeys().next()
        tf = None
        if TextFilter.objects.filter(filter_id=1).filter(filter_type='foot').filter(site_id=site_id).count() == 1:
            tf = TextFilter.objects.filter(filter_id=1).filter(filter_type='foot').filter(site_id=site_id)[0]
        else:
            tf = TextFilter()

        tf.filter_id = 1
        tf.filter_text = tt._max_group_reverse['grouping'].iterkeys().next()
        tf.filter_type = 'foot'
        tf.site_id = site_id
        tf.save()

headfoot(this_site)
    #print docs
