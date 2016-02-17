#python imports
import re
import urllib
import cgi
import sys
import config_file

#django imports
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.shortcuts import render, get_object_or_404
#from django.core.urlresolvers import reverse
from django import forms

class ConfigForm(forms.Form):
    universal_deny = forms.CharField(required=False,widget=forms.Textarea(attrs={'rows':3,'class': 'form-control'}))
    es_controller = forms.CharField(max_length = 100,widget=forms.TextInput(attrs={'class': 'form-control'}))
    crawler_instance_site_limit = forms.IntegerField(widget = forms.NumberInput(attrs={'class':'form-control'}))
    country_list = forms.CharField(widget=forms.Textarea(attrs={'rows':2, 'class':'form-control'}))
    es_instance = forms.CharField(max_length = 20,widget=forms.TextInput(attrs={'class': 'form-control'}))
    web_server_instance = forms.CharField(max_length = 20,widget=forms.TextInput(attrs={'class': 'form-control'}))
    crawler_instance = forms.CharField(max_length = 255,widget=forms.TextInput(attrs={'class': 'form-control'}))
    owners = forms.CharField(max_length=255, widget=forms.TextInput(attrs={'class': 'form-control'}))

    grouping = forms.CharField(max_length=255, widget=forms.TextInput(attrs={'class': 'form-control'}))


def index(request):
    config = config_file.get_config()
    
    if request.POST:
        if len(request.POST) > 0:
            for r in request.POST:
                config.set('bblio',r,str(request.POST[r]))
            config_file.set_config(config) 
    
    try:
        config.items('bblio')
    except:
        config.add_section('bblio')
    
    form = ConfigForm()
    for f in form.fields:
        try:
            form.fields[f].initial = config.get('bblio',str(f))
        except:
            config.set('bblio',f,'')
    config_file.set_config(config)    

    context = {'form' : form }
    
    return render(request, 'operations/admin.html', context)

def push_scrape(request):
    #from aws.scrapeMaster import copy_files
    #copy_files()
    from scraper.scrapeController import deploy
    deploy()
    
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    
