#!/usr/bin/env python
from elasticsearch import Elasticsearch
import re
import pprint
import sys
import os


host = '0.0.0.0:9200'
index_used = 'test-index'
print(host)
pp = pprint.PrettyPrinter(indent=4)
es = Elasticsearch(host)

def delete():
    print('Delete Index')
    es.indices.delete(index='_all')    

def show(index=index_used):
    data = es.indices.stats(index=index_used)['_all']['primaries']['docs']
    pp.pprint(data)
    return data

def delete(id,index=index_used): 
    es.delete(index=index_used,doc_type='legaltext',id=id) 

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
                            'analyzer':'my_analyzer'
                            },
                        }
                    }
                },
            }
    s.update({
        "settings":{
            "index":{
                "analysis" : {
                    "analyzer":{
                        "my_analyzer":{
                            "type":"custom",
                            "tokenizer": "standard",
                            "filter":["filter1"]
                            },
                        },
                    "filter" : {
                        "filter1": {
                            "type":"shingle",
                            "max_shingle_size":4,
                            },
                        "filter2": {
                            "type": "unique",
                            "only_on_same_position" : False
                            },
                        "suggestion_shingle": {
                            "type": "shingle",
                            "min_shingle_size": 2,
                            "max_shingle_size": 5
                            }
                        }
                    }
                } 
            }
        })

    res = es.indices.create(index=index,body=s)
    pp.pprint(res)
    autoindex()


def index(id,text,index=index_used):
    doc = {
            "text" : text,
            }

    res = es.index(index=index,doc_type='type1',body=doc,id=id)    
    pp.pprint(res)

def autoindex(indexName=index_used):
    index(1,'hello world',indexName)
    index(2,'world hello',indexName)
    index(3,'foo bar',indexName)
    index(4,'this is a long sentence that has hello world and world hello and more like hello worlds and more than you can hello. hello!',indexName)
    index(5,'hello foo world',indexName)
    index(6,'hello far far far far far far far far far far far far away world',indexName)
    index(7,'one two three four five',indexName)
    index(8,'two three four five',indexName)
    index(9,'three four five six',indexName)


def suggest():
    k = {
        "suggest" : {
            "text" : "helol",
            "simple_phrase" : {
                "phrase" : {
                    "field" : "text",
                    "size" : 5,
                    "real_word_error_likelihood" : 0.95,
                    "max_errors" : 0.3,
                    "gram_size" : 3,
                    "direct_generator" : [ {
                        "field" : "text",
                        "suggest_mode" : "always",
                        "min_word_length" : 2,
                        } ],
                    }
                }
            }
        }
    
    res = es.search(index='_all', body=k)
    pp.pprint(res)
    return res 

def searchtest():
    q = {
            #"fields" : "text",
            "query" : {
                #"query_string" : {
                #    "query" : 'hello world "hello world"'
                #    },
                "boosting" : {
                    "positive" : {
                        "term" : {
                            "text" : '"hello world"'
                            }
                        },
                    "negative_boost" : 0.2
                    }
               }
            }
    k = {
            "query":{
                "span_near" : {        
                    "clauses" : [
                        { "span_term" : { "text" : "hello" } },                         
                        { "span_term" : { "text" : "world" } },],
                    "slop" : 4,
                    "in_order" : "false",
                    "collect_payloads" : "false"
                    }
                }
            }
    
    q = { 'fields' :'text',
            'query' : {
                'query_string':{
                    'query' : '"hello world" OR hello world'
                    }
                }
            }
    res = es.search(index='_all', body=k)
    pp.pprint(res)
    return res

def search(search_term):
    q = {   
            "fields" : "text",
            "query": {
                "query_string": {
                    "query": search_term,
                                }               
                      },
            "highlight":{
                "pre_tags": ["<b>"],
                "post_tags":["</b>"],
            
            "fields": {
                "_all": {}
                }
             }
        }
    res = es.search(index='_all', body=q)
    pp.pprint(res)
    return res

def analyse():
    pp.pprint(es.indices.analyze(index_used,body='body used',analyzer='whitespace'))

def facet(index=index_used):
    q = {
            "query" : {
                "match_all" : {  }
                },
            "facets" : {
                "text" : {
                    "terms" : {
                        "field" : "text",
                        "size" : 40,
                        }
                    }
                }
            }

    res = es.search(index=index, body=q)['facets']
    pp.pprint(res)
    return res

if __name__ == '__main__':
    arg = sys.argv
    if len(sys.argv) > 1:
        if arg[1] == 'index':
            if len(arg) == 5:
                index(int(arg[2]),str(arg[3]),str(arg[4]))
            else:
                index(int(arg[2]),str(arg[3]))
        elif arg[1] == 'search':
            search(str(arg[2]))
        elif arg[1] == 'delete':
            delete()
        elif arg[1] == 'clear':
            clearcache()
        elif arg[1] == 'show':
            show()
        else:
            locals()[arg[1]]()
    else:
        print(search('hello',2))
