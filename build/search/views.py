#django imports
from django.shortcuts import render, get_object_or_404
from models import Document, Site

from lib2to3.fixer_util import Newline
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.forms.formsets import formset_factory
from django.forms.models import modelformset_factory
from django.core.urlresolvers import reverse
from django import forms

#python imports
import urllib
import re
import sys

#es controller imports
from es.YTHESController import YTHESController as ESController

import config_file

def get_country_list():
    config = config_file.get_config()
    cl = config.get('bblio','country_list')
    return ((x.split("|")[0], x.split("|")[1]) for x in cl.split(";"))

class CountryCheckboxes(forms.Form):
    country = forms.MultipleChoiceField(
            required=False,
            widget=forms.CheckboxSelectMultiple, 
            choices=get_country_list())

def get_selected_country_list(request):
    if not request.GET:
        return None
    selected_list = []
    all_selected = True
    for c in get_country_list():
        if c[0] in request.GET:
            selected_list.append(c[0])
        else:
            all_selected = False
    if not all_selected:
        return None
    return selected_list

def index(request):
    k=50
    context = {}

    boxes = CountryCheckboxes(initial={'country' : [cty[0] for cty in get_country_list()]})
    if 'q' in request.GET:
        q = request.GET['q'].encode('utf-8')
        p = 1
        if 'p' in request.GET:
            p = min(1, int(request.GET['p']))
        es = ESController()
        c = get_selected_country_list(request)
        context.update(es.search(q,c,k,p))
        context.update({
            'linklist' : pager(k,int(context['result_count']),p,10),
            'last_search' : q,
            'last_search_url' : str(reverse('search.views.index')) 
            + '?q=' + str(urllib.quote(q)),
            'page' : p+1 })
        if c:
            context.update({'custom' : True})
            boxes = CountryCheckboxes(initial={'country':c})
    else:
        q = ''
    context.update({'form':boxes})
 
    return render(request, 'search/index.html',context)


def index2(request):
    k=50
    if 'q' in request.GET:
        q = request.GET['q'].encode('utf-8')
        print(q)
        if 'p' in request.GET:
            if int(request.GET['p']) == 0:
                p = 1
            p = int(request.GET['p']) - 1
        else:
            p = 0
        import search1 #current es search module
        context = search1.search(q,k,p*k)
    else:
        return HttpResponseRedirect(reverse('search.views.index'))
    print(context['result_count']) 
    context.update({'linklist':pager(k,int(context['result_count']),p,10)})
    context.update({'last_search':q})
    context.update({'last_search_url':str(reverse('search.views.index')) 
        + 'search/?q=' + str(urllib.quote(q))})
    return render(request, 'search/index.html',context)

def autocomplete(request):
    if 'term' in request.GET:
        term = request.GET['term'].encode('utf-8')
        import autocomplete1
        return HttpResponse(str(autocomplete1.get_autocomplete(term)))
    return HttpResponse("NO!!!")

def delete(request, site_id):
    if not request.user.is_staff:
        raise Http404
    else:
        Document.objects.filter(site_id=int(site_id)).delete()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def testsearch(request,query,page=1):
    esquery = urllib.unquote_plus(query)
    context = es.search(esquery,100,100*(int(page)-1))
    TestingFormSet = formset_factory(TestingFormResult,extra=0)
    form_list= []

    for r in context['result_list']:
        d = int(r['id'].decode('utf-8')) 
        f = {'document': d,'score':0}
        #score = TestingResult.objects.filter(searchterm=esquery,testinggroup=tes
        #f.update('score': 0)
        form_list.append(f)

    list = zip(formset, context['result_list'])
    context.update({'list':list})
    context.update({'last_search':esquery})
    context.update({'linklist':pager(100,int(context['result_count']),page,10)})
    context.update({'page':page})
    return render(request, 'search/testing.html',context)

def testing(request):
    if 'search_term' in request.POST:
        query = str(request.POST['search_term'])
        url = reverse('search.views.testsearch', args=(urllib.quote_plus(query),1,))
        return HttpResponseRedirect(url)
    else:
        context = {}
    return render(request, 'search/testing.html',context)

def pager(size,result_count,page,linkcount):
    lastpage = int(result_count/size) + 1

    if lastpage < linkcount:
        return range(1,lastpage+1)
    elif page < linkcount/2:
        return range(1,linkcount+1)
    elif page > (lastpage - (linkcount/2)):
        return range(lastpage-linkcount,lastpage+1)
    else:
        return range(page-(linkcount/2),page+(linkcount/2)+1)
        
def testing_input(request):
    TestingFormSet = formset_factory(TestingFormResult,extra=0)
    if request.method == 'POST' and 'search_term' not in request.POST:
        request.encoding = 'utf-8'
        pageset = TestingFormPage(request.POST,prefix='page')
        formset = TestingFormSet(request.POST,prefix='doc')
        if not formset.is_valid():
            return HttpResponse(str(formset.errors))

        if formset.is_valid() and pageset.is_valid():
            searchterm = pageset.cleaned_data['searchterm']
            testinggroup = int(pageset.cleaned_data['testinggroup'])
            if TestingGroup.objects.filter(pk=testinggroup).count() == 0:
                TestingGroup(id=testinggroup).save()
            for form in formset:
                document = int(form.cleaned_data['document'])
                score = int(form.cleaned_data['score'])
                doc = TestingResult.objects.filter(testinggroup=testinggroup).filter(searchterm=searchterm).filter(document=document)
                if doc.count() > 0:
                    if score == 0:
                        doc.delete()
                    else:
                        doc.update(score=score)
                        #doc.save()
                elif score > 0:
                    TestingResult(searchterm=searchterm,testinggroup=TestingGroup.objects.get(pk=testinggroup),document=Document.objects.get(pk=document),score=score).save()
            return HttpResponse('TestingGroup %s, SearchTerm %s saved' % (str(testinggroup), searchterm))
        return HttpResponse('form is not valid')
    else:
        return HttpResponsee('No POST request')

def scraped(request, site_id):
    site = Site.objects.get(pk=site_id)
    if 'source_denyParse' in request.POST:
        form = AdminURLListForm(request.POST)
        if form.is_valid():
            form_deny = form.cleaned_data['source_denyParse']
        
            if form_deny != site.source_denyParse:
                docs = Document.objects.filter(site=site)
                site.source_denyParse=form_deny
                site.save()
                denys = form_deny.split(';')
                for deny in denys:
                    d = docs.filter(urlAddress__contains=deny)
                    d.update(isUsed=1)

    d = Document.objects.filter(site_id=site_id).values('id','urlAddress','isUsed').order_by('isUsed','urlAddress')
    form = AdminURLListForm({'source_denyParse': Site.objects.get(pk=site_id).source_denyParse})
    context = {'site_id':site_id,'docs':d,'form':form}

    return render(request, 'search/scraped.html',context)

def result(request, key_id):
    d = get_object_or_404(Document, pk=key_id)
    return HttpResponse(d.document_text)

def testscrape(request):
    return render(request, 'search/testscrape.html')    
