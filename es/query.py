#!/usr/bin/env python
from elasticsearch import Elasticsearch
import getdoc as docdata
import re
import pprint
import sys
sys.path.append('/home/ec2-user/bblio/build/')
sys.path.append('/home/ec2-user/bblio/aws/')
import ec2
import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'Build.settings'
from django.forms.models import model_to_dict
import time
import subprocess
from django.db import connection
from search.models import Document

host = str(ec2.getESip()) + ':9200'
print(host)
def query():
    es = Elasticsearch(host)

    q = {
            "query" : {
                "match_all" : {  }
                },
            "facets" : {
                "text" : {
                    "terms" : {
                        "field" : "text",
                        "size" : 1
                        }
                    }
                }
            }



    res = es.search(index="legal-index", body=q)    
    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(res)

if __name__ == '__main__':
    query()
