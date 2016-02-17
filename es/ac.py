#!/usr/bin/env python
from elasticsearch import Elasticsearch
import re
import pprint
import sys
import os


host = '0.0.0.0:9200'
index_used = 'ac-index'
print(host)
pp = pprint.PrettyPrinter(indent=4)
es = Elasticsearch(host)

def facet(index='test-index'):
    q = {
            "query" : {
                "match_all" : {  }
                },
            "facets" : {
                "text" : {
                    "terms" : {
                        "field" : "text",
                        "size" : 40
                        }
                    }
                }
            }

    res = es.search(index=index, body=q)['facets']['text']['terms']
    pp.pprint(res)
    return res

def delete():
    print('Delete Index')
    es.indices.delete(index=index_used)    
    return

def show(index=index_used):
    data = es.indices.stats(index=index_used)['_all']['primaries']['docs']
    pp.pprint(data)
    return data

def index(id,text,index=index_used):
    doc = {
            "text" : id,
            "suggest" : text
            }

    res = es.index(index=index,doc_type='type1',body=doc,id=id)    
    pp.pprint(res)
    return

def create_index(index=index_used):
    try:
        es.indices.delete(index=index)
    except:
        pass

    s = {
            'mappings':{
                'type1':{
                    '_source': { 'enabled': 'false'},
                    'properties':{
                        'text':{
                            'type':'string',
                            },
                        "suggest" : { 
                            "type" : "completion",
                            "preserve_separators" : True
                            },
                        }
                    }
                },
            }
    res = es.indices.create(index=index,body=s)
    pp.pprint(res)
    facet_list = facet()
    for id, f in enumerate(facet_list):
        es.index(index=index,doc_type='type1',body={"text":id,"suggest":f['term']},id=id)

    return

if __name__ == '__main__':
    arg = sys.argv
    if len(sys.argv) > 1:
        locals()[arg[1]]()
