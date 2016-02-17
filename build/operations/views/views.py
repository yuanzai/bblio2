#python imports
import re
import urllib
import cgi
import sys

#django app imports
from search.models import Document, Site, TestingResult, TestingGroup, Phrase
from operations.forms import TestingFormPage, TestingFormResult, AdminURLListForm, SiteForm

#django imports
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.shortcuts import render, get_object_or_404
from django.forms.formsets import formset_factory
from django.forms.models import modelformset_factory, modelform_factory
from django.core.urlresolvers import reverse
from django.core.management import call_command
from django import forms
from django.forms.models import model_to_dict

#es import
from es.YTHESController import YTHESController as ESController

#crawler import
import scraper.scrapeController

#distributed import
import aws.scrapeMaster

def index(request):
    context = {}
    return render(request,'operations/index.html',context)

def phrases(request):
    PhraseForm = modelform_factory(Phrase)
    
    if request.method == 'POST':
        """
        form = PhraseForm(request.POST)
        form.save()
        """
        phrases = request.POST['phrase'].encode('ascii','ignore').split('\r\n')
        for p in phrases:
            if p:
                p = p.decode('utf-8')
                p = p.strip()
                p = p.replace('-',' ')
                p = p.lower()
                if ' ' in p:
                    if Phrase.objects.filter(phrase=p).count() == 0:
                        print('save: ' + p)
                        newphrase = Phrase()
                        newphrase.phrase = p
                        newphrase.save()

    form = modelform_factory(Phrase,
            widgets={ 'phrase' : forms.Textarea(attrs={'class': 'form-control'})})
    
    phrases = Phrase.objects.all()

    context = { 'phrases' : phrases, 'form' : form }
    return render(request, 'operations/phrases.html',context)

def tester(request,query='',testinggroup=1,page=1):
    context = {}
    if query:
        esquery = urllib.unquote_plus(query)
        if page == 0:
            page = 1
        if request.method == 'POST':
            TestingFormSet = formset_factory(TestingFormResult,extra=0)
            formset = TestingFormSet(request.POST,prefix='doc')
            if not formset.is_valid():
                return HttpResponse(str(formset.errors))

            if formset.is_valid():
                if TestingGroup.objects.filter(pk=testinggroup).count() == 0:
                    TestingGroup(id=testinggroup).save()
                docs = TestingResult.objects.filter(testinggroup=testinggroup).filter(searchterm=esquery)
                for form in formset:
                    document = int(form.cleaned_data['document'])
                    score = None

                    if form.cleaned_data['score'] == 0 or form.cleaned_data['score']:
                        score = int(form.cleaned_data['score'])
                    
                    doc = docs.filter(document_id=document)
                    if len(doc) > 0:
                        if score or score ==0:
                            doc.update(score=score)
                        else:
                            doc.delete()
                    elif score or score ==0:
                        TestingResult(searchterm=esquery,
                                testinggroup_id=testinggroup,
                                document_id=document,
                                score=score).save()
        
        context = es.search(esquery,100,100*(int(page)-1))
        TestingFormSet = formset_factory(TestingFormResult,extra=0)
        
        form_list= []
        scores = TestingResult.objects.filter(searchterm=esquery).filter(testinggroup_id=testinggroup)
        count = 1
        for r in context['result_list']:
            d = int(r['id'].decode('utf-8')) 
            f = {'document': d}
            s = scores.filter(document_id=d)
            if len(s) >0:
                score = s[0].score
            else:
                score = None
            f.update({'score': score})
            r.update({'count': count})
            count = count + 1
            form_list.append(f)
    
        formset = TestingFormSet(initial=form_list,prefix='doc')
        list = zip(formset, context['result_list'])
        context.update({'formset':formset})
        context.update({'list':list})
        context.update({'last_search':esquery})
        context.update({'testinggroup':testinggroup})
        context.update({'page':page})
        context.update({'linklist':pager(100,int(context['result_count']),page,10)})
    return render(request, 'operations/tester.html',context)


def pager(size,result_count,page,linkcount):
    lastpage = int(result_count/size) + 1
    if lastpage < linkcount:
        return range(1,lastpage+1)
    elif int(page) < linkcount/2:
        return range(1,linkcount+1)
    elif int(page) > (lastpage - (linkcount/2)):
        return range(lastpage-linkcount,lastpage+1)
    else:
        return range(int(page)-(linkcount/2),int(page)+(linkcount/2)+1)
        
