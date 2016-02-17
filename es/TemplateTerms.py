"""
import sys
sys.path.append('/home/ec2-user/bblio/build/')

import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'Build.settings'

from django.db import connection
from YTHESController import YTHESController as ESController
from scraper.scrapeController import link_extractor
from search.models import Site, Document
"""
from collections import OrderedDict
#import re

#import difflib

class TemplateTerms(object):
    _text_list = None
    _max_count = None
    _max_group = None
    _max_group_reverse = None
    _threshold = None

    def __init__(self, text_list):
        self._text_list = text_list


    def generate(self, threshold_percent):
        max_len = max([len(l) for l in self._text_list if l != ''])
        self._threshold = int(len(self._text_list)*threshold_percent)
        self._max_group = self.bi(1, max_len, self._text_list, self._threshold)
        self._max_group_reverse = self.bi(1, max_len, self._text_list, self._threshold, False)
        if self._max_group['max_count'] < self._threshold: self._max_group = None
        if self._max_group_reverse['max_count'] < self._threshold: self._max_group_reverse = None
    
    def grouper(self, text_list, char, asc):
        char_dict = {}
        for t in text_list:
            if len(t) < char:
                char_key = t
            else:
                if asc:
                    char_key = t[0:char]
                else:
                    char_key = t[-char:]
            
            count = 1
            this_list = [t]
            if char_key in char_dict:
                count = char_dict[char_key]['count'] + count
                this_list.extend(char_dict[char_key]['list'])
            
            char_dict.update({ char_key:{ 'count' : count, 'list' : this_list}})
        od = OrderedDict(sorted(char_dict.items(), key=lambda t: t[1]))
        items = od.items() 
        items.reverse()
        return { 'max_count' : OrderedDict(items).items()[0][1]['count'], 'grouping' : OrderedDict(items)}

    def bi(self, lo, hi, text_list, threshold, asc = True):
        if lo + 1 == hi:
            return self.grouper(text_list, lo, asc)

        group = self.grouper(text_list, int((lo + hi)/2), asc)
        if group['max_count'] >= threshold:
            return self.bi(int((lo + hi)/2), hi, text_list, threshold, asc)
        else:
            return self.bi(lo, int((lo + hi)/2), text_list, threshold, asc)

"""
testlist = ['aaaaa1234567bbbbb','aaaaa23456bbbbbb','aaaaa3456789bbbbb','aaaaa43579bbbbb','aaaaa54680bbbbb','aaa123ccc','aaa234ccc','bbbbb1313ccc','bbbbbb14141ccc','bb1313']
tt = TemplateTerms(testlist)

tt.generate(.5)
print tt._max_group
"""
