#!/usr/bin/env python

import re
import pprint
import sys
sys.path.append('/home/ec2-user/bblio/build/')
sys.path.append('/home/ec2-user/bblio/aws/')
import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'Build.settings'
import time
from search.models import Document
import es
from io import StringIO, BytesIO
from lxml import etree

es = es.get_es()
_xpath =  "body/descendant::*[not(self::script|self::link)]"
_index =  "legal-index-html"
_doc_type = "legal-text-html"

def get_tree(text):
    text = re.sub('<strong>','',text)
    text = re.sub('</strong>','',text)
    text = re.sub('\n','',text)
    text = re.sub('\t','',text)
    text = re.sub(r'\s+',' ',text)
    parser = etree.HTMLParser()
    tree = etree.parse(StringIO(text.encode('utf-8').decode('utf-8')), parser)
    return tree

def get_body_html(text):
    tree = get_tree(text)
    result = tree.xpath(_xpath)
    body = []
    for s in result:
        body.append(etree.tostring(s))
    return '\n'.join(body)

def text_parse(text):
    tree = get_tree(text)
    result = tree.xpath(_xpath + "/text()")
    return result

def get_doc(Document):
    doc = {
            "title" : Document.title,
            "urlAddress" : Document.urlAddress,
            "text" : ' '.join(text_parse(Document.document_html)),
            }
    return doc

def get_mapping():
    m = {
            "mappings":{
                _doc_type:{
                    "properties":{
                        "text":{
                            "type":"string",
                            "analyzer":"my_analyzer"
                            },
                        }
                    }
                },
            "settings":{
                "index":{
                    "analysis" : {
                        "analyzer":{
                            "my_analyzer":{
                                "tokenizer": "standard",
                                "filter":["standard","lowercase","porter_stem","filter1"],
                                },
                            },
                        "filter" : {
                            "filter1": {
                                "type":"shingle",
                                "min_shingle_size":2,
                                "max_shingle_size":4,
                                "output_unigrams":"true",
                                },
                            },
                        }
                    }
                }
            }
        
    return m

def delete_index():
    try:
        es.indices.delete(index=_index)
    except:
        pass

def delete(id): 
    es.delete(index=_index,doc_type=_doc_type,id=id)

def index_one(id):
    es = Elasticsearch(host)
    d = Document.object.get(pk=id)
    doc = get_doc(d)
    es.index(index=_index,doc_type=_doc_type,body=doc,id=id)

def index(n=0,end=1000,k=1000):
    if es.indices.exists(index=_index):
        print('index found!')
    else:
        es.indices.create(index=_index,body=get_mapping())
    
    if end == 0:
        doc_count = Document.objects.count()
    else:
        doc_count = end
    while True:
        dList = Document.objects.filter(update_group=1).filter(isUsed=0)
        if n > doc_count:
            dList = dList[n:doc_count]
        else:
            dList = dList[n:int(n)+k]
        print(n) 
        docs = []
        for d in dList:
            try:
                header = { "index" : { "_index" : _index, "_type" : _doc_type, "_id" : d.id } }
                doc = get_doc(d)
                docs.append(header)
                docs.append(doc)
            except:
                print 'Fail to parse %s',str(d.id)

        es.bulk(body=docs,index=_index, doc_type=_doc_type)

        n =n + k
        if n % 2000 == 0:
            dList = None
            es.indices.clear_cache(index=_index)
        if n >= doc_count:
            break

def search(search_term,result,start_result=0):
    es = Elasticsearch(host)
    q = {   
            "fields" : ["text"],
            "from" : start_result,
            "size" : result,
            "query": {
                "query_string": {
                    "query": search_term,
                                }               
                      },
            "highlight": {
                 "fields": {
                    "text": {"fragment_size" : 100, "number_of_fragments": 5}
                        }
                    } 
             }
    res = es.search(index=_index, body=q)    
    r =  res['hits']['hits']
    l = []
    for re in r:
        d = {"urlAddress" : re['fields']['urlAddress'],
             "title" : str(re['fields']['title'][3:-2].decode('utf-8')),
             "id" : re['_id'],
             "score" : re['_score'],}
        if d['title'] == '':
            d['title'] = d['urlAddress']
        try:
            d.update({"highlight" : re['highlight']['text']})
        except:
            pass

        l.append(d)
    return {'result_list': l,
            'result_count': res['hits']['total']}

if __name__ == '__main__':
    arg = sys.argv
    if len(sys.argv) > 1:
        locals()[arg[1]]()
