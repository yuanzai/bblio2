#!/usr/bin/env python
from elasticsearch import Elasticsearch
import re
import pprint
import sys
sys.path.append('/home/ec2-user/bblio/build/')
sys.path.append('/home/ec2-user/bblio/aws/')
import ec2
import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'Build.settings'
from django.forms.models import model_to_dict
from django.db import connection
from search.models import Document, Site

class BaseESController(object):
    
    _es_index = None
    _es_autocomplete_index = None
    _doc_type = None

    def __init__(self, local=True):
        if not self._es_index: 
            raise ESControllerError("Index not defined")

        self._host = str(ec2.getESip()) + ':9200'
        if local:
            self._es = Elasticsearch()
        else:
            self._es = Elasticsearch(self._host)

    def clear_cache(self):
        self._es.indices.clear_cache()

    def delete_index(self):
        self._es.indices.delete(index=self._es_index)

    def delete_one_doc(self,doc_id):
        try:
            self._es.delete(index=self._es_index,doc_type=self._doc_type,id=doc_id)
        except:
            pass

    def delete_site_id_from_es(self, site_id):
        res = self._es.search(
                index=self._es_index, 
                body = {
                    "query" : {
                        "match_all" : {}
                        },
                    "size": self.get_document_count_for_site_id(site_id),
                    "filter" : {
                        "term": {"site_id" : site_id}
                        }
                    })
        for r in res['hits']['hits']:
            self.delete_one_doc(int(r['_id']))
    
    def get_document_count_by_site(self):
        res = self._es.search(
                index=self._es_index,
                body = {
                    "query" :{
                        "match_all" :{}
                        },
                    "facets":{
                        "site_id":{
                            "terms" :{
                                "field": "site_id",
                                "size": 1000
                                }
                            }
                        }
                    }
                )
        site_dict = {}
        for r in res['facets']['site_id']['terms']:
            site_dict.update({ r['term'] : r['count']})
        return site_dict

    def get_document_count_for_site_id(self, site_id):
        res = self._es.search(
                index=self._es_index, 
                body = {
                    "query" : {
                        "match_all" : {}
                        },
                    "filter" : {
                        "term": {"site_id" : site_id}
                        }
                    })
        return res['hits']['total']

    def index_one_doc(self, Document):
        raise ESControllerError("Method not defined")
        return

    def index_site_id(self, site_id):   
        docs = Document.objects.filter(site_id=site_id).filter(isUsed=0)
        for id, doc in enumerate(docs):
            import time
            if id % 50 == 0:
                time.sleep(1)
            self.index_one_doc(doc)
            print('Indexing - ' + str(doc.id))

    def get_one_doc(self, id):
        return self._es.get(index=self._es_index,doc_type=self._doc_type,id=int(id))

    def search(self, search_term, 
            results_per_page=10, 
            current_page=1):
        raise ESControllerError("Method not defined")
        return
    
    def get_document_count(self):
        #gets the document count in the main index
        try:
            return self._es.indices.stats(index=self._es_index)['_all']['primaries']['docs']['count']
        except:
            return None
    
    def index_autocomplete(self):
        raise ESControllerError("Method not defined")
        return

    def delete_autocomplete(self):
        try:
            self._es.indices.delete(index=self._es_autocomplete_index)
        except:
            pass

    def get_autocomplete(self, search_term): 
        raise ESControllerError("Method not defined")
        pass

class ESControllerError(Exception):

    def __init__(self, *args):
        self.error_message = args[0]
        pass

    def __str__(self):
        return self.error_message
