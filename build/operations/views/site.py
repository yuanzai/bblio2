#python imports
import re
import urllib
import cgi
import sys
import random, string
from urlparse import urlparse

#django app imports
from search.models import Document, Site, TestingResult, TestingGroup, Phrase
from operations.forms import TestingFormPage, TestingFormResult, AdminURLListForm, SiteForm

#django imports
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.shortcuts import render, get_object_or_404
from django.forms.formsets import formset_factory
from django.forms.models import modelformset_factory, modelform_factory
from django.core.urlresolvers import reverse
from django import forms
from django.forms.models import model_to_dict
from django.db.models import Count
from django.template.loader import get_template


#es import
from es.YTHESController import YTHESController as ESController

#crawler import
import scraper.scrapeController

#distributed import
import aws.ec2

#import config
import config_file

def site(request, site_id):
    context = {
                'doc_count' : 0,
                'zero_count' : 0,
                'docs': 0,
                'running' : 0}
    site = None

    if site_id !='0': 
        site = Site.objects.get(pk=site_id)
        if not scraper.scrapeController.get_jobs_for_site(site_id):
            site.running=0
            site.save(update_fields=['running'])
        elif scraper.scrapeController.get_jobs_for_site(site_id) == 'finished':
            site.running=0
            site.save(update_fields=['running'])

    if request.method == 'POST':
        site_form  = SiteForm(request.POST,instance=site)
        if site_form.is_valid():
            new_site = site_form.save()
            if 'crawl' in request.POST:
                if request.POST['crawl']=='yes':
                    crawl(request, new_site.id)
            
            if site_id == '0':
                return HttpResponseRedirect(reverse('operations:site', 
                    kwargs={ 'site_id' : new_site.id}))
        else:
            return HttpResponse('Error fields: ' + str(site_form.errors))
    
    if site_id !='0':
        es = ESController()
        site = Site.objects.get(pk=site_id)
        d = (Document.objects.filter(site_id=site_id)
                .values('id','urlAddress','isUsed')
                .order_by('isUsed','urlAddress'))

        context.update({
            'doc_count' : d.count(),
            'zero_count' : Document.objects.filter(site_id=site_id).filter(isUsed=0).count(),
            'docs':d,
            'running' : site.running})

        try:
            context.update({'index_count' : es.get_document_count_for_site_id(site_id)})
        except:
            pass

        try: 
            context.update({'jobid': site.jobid,
                            'instance_ip': aws.ec2.getInstanceFromInstanceName(site.instance).ip_address})
        except:
            pass
    site_form = SiteForm(instance=site)
    context.update({
            'site_id':site_id,
            'site_form':site_form,})
    
    #template = get_template('operations/site.html')
    #return template.render(context, request)
    return render(request, 'operations/site.html',context)    

def run_deny_params(site_id):
    denys = Site.objects.get(pk=site_id).deny_parameters.split(';')
    for i,d in enumerate(denys):
        if "r'" in str(d[0:2]) and "'" in str(d[-1]):
            denys[i] = d[2:-1]

    denys = [i for i in denys if i != '']
    universal_deny = config_file.get_config().get('bblio','universal_deny').split(';')
    universal_deny = [i for i in universal_deny if i != '']
    denys.extend(universal_deny)
    
    host_regex= None
    source_allowed_domains = Site.objects.get(pk=site_id).source_allowed_domains
    
    if not source_allowed_domains:
        host_regex = re.compile('')
    else:
        regex = r'^(.*\.)?(%s)$' % '|'.join(re.escape(d) for d in source_allowed_domains.split(";"))
        host_regex = re.compile(regex)

    for doc in Document.objects.filter(site_id=site_id):        
        if any([re.search(re.compile(d), doc.urlAddress) for d in denys if d != None]):
            doc.isUsed = 6
            doc.save()
        if not bool(host_regex.search(urlparse(doc.urlAddress).hostname)):
            doc.isUsed=6
            doc.save()
    

def sites(request):
    sites = Site.objects.all()
    site_list = []
    es = ESController()

    try:
        site_doc_count = es.get_document_count_by_site()
    except:
        site_doc_count = {}

    owners = config_file.get_config().get('bblio','owners').split(';')
    scoreboard = {}
    for o in owners:
        if o != '':
            scoreboard.update({o: {'doc':0, 'site':0}})
    for site in sites:
        s = model_to_dict(site)
        s.update({'doc_count': Document.objects.filter(site_id=site.id).count()})
        s.update({'zero_count': Document.objects.filter(site_id=site.id).filter(isUsed=0).count()})
        try:
            doc = site_doc_count[site.id]
            s.update({'index_count':doc})
            if site.owner:
                scoreboard[site.owner]['site'] += 1
                scoreboard[site.owner]['doc'] += doc
        except:
            s.update({'index_count': 0})

        site_list.append(s)
    if not site_doc_count:
        d = Document.objects.filter(isUsed=0).values('site__owner').annotate(zero_count=Count('site__owner'))
        scoreboard= d

    context = {'sites':site_list, 'score':scoreboard}
    return render(request, 'operations/sites.html',context)

# input code
def delete(request, site_id):
    Site.objects.get(pk=site_id).delete()
    return HttpResponseRedirect(reverse('sites'))

# crawler code
def crawl(request, site_id):
    import time
    site = Site.objects.get(pk=site_id)
    if site.instance == '' or not site.instance:
        return HttpResponse("No working instance selected")
     
    if scraper.scrapeController.get_jobs_for_site(site_id)=='Running':
        return HttpResponse("Crawler is running")
    try:
        c_dict = scraper.scrapeController.get_job_status_count_for_instance(site.instance) 
        count = int(c_dict['running']) + int(c_dict['pending'])
    except:
        count = 0
    if count < int(config_file.get_config().get('bblio','crawler_instance_site_limit')):
        ret = scraper.scrapeController.curl_schedule_crawl(site_id, site.instance)
        if 'jobid' in ret:
            site.jobid = ret['jobid']
            site.save()
        else:
            return HttpResponse("Error when scheduling job")
    else:
        return HttpResponse("Worker instance is full. Please try another instance")
    
    site.running=2
    site.save()
    time.sleep(3)
    return HttpResponseRedirect(reverse('operations:site', 
        kwargs={ 'site_id' : site_id}))

def crawl_cancel(request, site_id):
    if not scraper.scrapeController.curl_cancel_crawl(site_id):
        return HttpResponse("Cancel Failed")
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def crawl_not_running(request, site_id):
    site = Site.objects.get(pk=site_id)
    site.running = 0
    site.save()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

#database document code
def document(request,doc_id):
    import HTMLParser
    es = ESController()
    doc = Document.objects.get(pk=doc_id)
    context = {
            'html': '<code>' + re.sub('\n','</code>\n<code>',cgi.escape(es.get_body_html(doc.document_html))) + '</code>',
            'parsed_text' : es.text_parse(doc),
            'parsed_title' : es.title_parse(doc.document_html)
            }

    return render(request, 'operations/document.html',context)


def document_reset_to_zero(request,site_id):
    Document.objects.filter(site_id=site_id).update(isUsed=0)
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def document_duplicate_filter(request,site_id):
    docs = Document.objects.filter(site_id=site_id).filter(isUsed=0)
    urlList = docs.values_list('urlAddress',flat=True).distinct()
    run_deny_params(site_id)
    
    for url in urlList:

        #pure duplicate
        #if docs.filter(urlAddress=url).count() > 1:
        #    first_id = docs.filter(urlAddress=url)[0].id
        #    docs.filter(urlAddress=url).exclude(pk=first_id).update(isUsed=2)
        #    continue
        
        #https filter
        if url[:5] == 'https':
            url_http = url[:4] + url[5:]
            if url_http in urlList:
                docs.filter(urlAddress=url).update(isUsed=3)
                continue

        #www filter
        if url[:11] == 'https://www':
            url_www = 'https://' + url[12:]
        elif url[:10] == 'http://www':
            url_www = 'http://' + url[11:]
        else:
            url_www = None

        if url_www:
            if url_www in urlList:
                docs.filter(urlAddress=url_www).update(isUsed=4)
                continue

        #slash filter
        if url[-1:] == '/':
            url_slash = url[:-1]
            if url_slash in urlList:
                docs.filter(urlAddress=url).update(isUsed=5)

    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def document_delete(request, site_id):
    Document.objects.filter(site_id=site_id).delete()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

#elasticsearch code
def es_index_site(request, site_id):
    import threading
    t = threading.Thread(target=index_process,args=(site_id,))
    t.setDaemon(True)
    t.start()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def index_process(site_id):
    es = ESController()
    es.index_site_id(site_id)

def es_remove_site_from_index(request, site_id):
    es = ESController()
    es.delete_site_id_from_es(site_id)
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

#others
def tree(request):
    context = {}
    if request.method == 'POST':
        url = request.POST['url']
        level = int(request.POST['level'])
        linkno = request.POST['linkno']
        parse_parameters = None
        follow_parameters = None
        deny_parameters = None
        source_allowed_domains = None
        if request.POST['parse_parameters'] != '':
            parse_parameters = request.POST['parse_parameters']
        if request.POST['follow_parameters'] != '':
            follow_parameters = request.POST['follow_parameters']
        if request.POST['deny_parameters'] != '':
            deny_parameters = request.POST['deny_parameters']
        if request.POST['source_allowed_domains'] != '':
            source_allowed_domains = request.POST['source_allowed_domains']
        
        context = {'level' : level + 1} 
        linklist = []
        if level == 0:
            urllist = url.split(";")
            for eachurl in urllist:
                linklist.append({
                    'url':eachurl,
                    'allow':'followed',
                    'linkno':''.join([random.choice(string.ascii_letters + string.digits) for n in xrange(32)])})
        else:
            linklist  = scraper.scrapeController.link_extractor(url,parse_parameters,follow_parameters,deny_parameters,source_allowed_domains)
        context.update({'list':linklist})
    return render(request, 'operations/tree.html',context)

if __name__ == '__main__':
    arg = sys.argv    
    if len(sys.argv) > 1:
        if arg[1] == 'deny':
            run_deny_params(arg[2])

