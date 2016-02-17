from django import forms
from django.forms.formsets import BaseFormSet
from django.forms import Textarea, TextInput, Select
from search.models import TestingResult,Site
from aws.ec2 import getCrawlerInstances
import config_file
from scraper.scrapeController import get_job_status_count_for_instance
from search.views import get_country_list 

class TestingForm(forms.ModelForm):
    class Meta:
        model = TestingResult
        fields = ['document', 'score', 'testinggroup', 'searchterm']

class SiteForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(SiteForm, self).__init__(*args, **kwargs)
        print "init"
        running_limit = config_file.get_config().get('bblio','crawler_instance_site_limit')
    
        instance_list = []
        grouping_list = [('works','works'),('works dirty','works dirty'),('WIP','WIP'),('error','error'),('condemned','condemned'),('start','start'), ('test','test')]
        print "trying"
        for i in getCrawlerInstances():
            print i
            dic = get_job_status_count_for_instance(i.id)
            count = int(dic['pending']) + int(dic['running'])
            instance_list.append({'name':i.id,'choice_name': i.id + ' ' + str(count) + '/' + str(running_limit)})
        print instance_list
        print "tried"
        instance_list.append({'name':'','choice_name':''})
        instance_choices = ((i['name'],i['choice_name']) for i in instance_list)
        print "instanced"
        self.fields['instance'].widget = Select(attrs={'class': 'form-control input-sm'}, choices=instance_choices)
        self.fields['jurisdiction'].widget = Select(attrs={'class': 'form-control input-sm'}, choices=get_country_list())
        self.fields['owner'].widget = Select(attrs={'class': 'form-control input-sm'}, choices=[(o, o) for o in config_file.get_config().get('bblio','owners').split(';')])
        self.fields['grouping'].widget = Select(attrs={'class': 'form-control input-sm'}, choices=[(g,g) for g in config_file.get_config().get('bblio','grouping').split(';')])
    
    class Meta:
        model = Site
       
        fields = [
                'name','grouping','depthlimit','jurisdiction',
                'source_allowed_domains',
                'source_start_urls',
                'source_allowParse',
                'source_denyParse',
                'source_allowFollow',
                'source_denyFollow',
                'parse_parameters',
                'follow_parameters',
                'deny_parameters',
                'instance',
                'owner'
                ]
        widgets = {
                'name': TextInput(attrs={'class': 'form-control'}),
                'depthlimit': TextInput(attrs={'size':5, 'class': 'form-control'}),

                #'jurisdiction': TextInput(attrs={'class': 'form-control'}),

                'source_allowed_domains': Textarea(
                    attrs={'cols': 80, 'rows': 2, 'class': 'form-control'}),
                'source_start_urls': Textarea(
                    attrs={'cols': 80, 'rows': 2, 'class': 'form-control'}),
                'source_allowParse': Textarea(
                    attrs={'cols': 80, 'rows': 2, 'class': 'form-control'}),
                'source_denyParse': Textarea(
                    attrs={'cols': 80, 'rows': 2, 'class': 'form-control'}),
                'source_allowFollow': Textarea(
                    attrs={'cols': 80, 'rows': 2, 'class': 'form-control'}),
                'source_denyFollow': Textarea(
                    attrs={'cols': 80, 'rows': 2, 'class': 'form-control'}),
                'parse_parameters': Textarea(
                    attrs={'cols': 80, 'rows': 4, 'class': 'form-control input-sm'}),
                'follow_parameters': Textarea(
                    attrs={'cols': 80, 'rows': 2, 'class': 'form-control input-sm'}),
                'deny_parameters': Textarea(
                    attrs={'cols': 80, 'rows': 4, 'class': 'form-control input-sm'}),
                }


class AdminURLListForm(forms.Form):
    source_denyParse = forms.CharField(required=False,widget=forms.TextInput(attrs={'size': '120'}))

class TestingFormResult(forms.Form):
    document = forms.IntegerField(widget=forms.HiddenInput())
    score = forms.IntegerField(required=False,widget=forms.TextInput(attrs={'size': '4'}))

class TestingFormPage(forms.Form):
    testinggroup = forms.IntegerField()
    searchterm = forms.CharField()
