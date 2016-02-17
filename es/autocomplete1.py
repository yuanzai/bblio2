#!/usr/bin/env python
import re
import pprint
from es import get_es
import sys
from search.models import Phrase
import json
pp = pprint.PrettyPrinter(indent=4)
es = get_es()


def get_autocomplete(term):
    s = {
            "text-suggest" : {
                "text" : term,
                "completion" : {
                    "field" : "suggest"
                    }
                }
            }
    res = es.suggest(index='autocomplete',body=s)
    result = []
    for r in res['text-suggest'][0]['options']:
        r_dict = {
                "id": r['text'].encode('utf-8'),
                "label": r['text'].encode('utf-8'),
                "value": r['text'].encode('utf-8')
                }
        result.append(r_dict)
    pp.pprint(result)
    return json.dumps(result)

def delete_autocomplete():
    try:
        es.indices.delete(index='autocomplete')
    except:
        pass

def index_autocomplete():
    s = {
            'mappings':{
                'autocompleteterm':{
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
    es.indices.create(index='autocomplete',body=s)
    facet_list = facet()
    for id, f in enumerate(facet_list):
        es.index(index='autocomplete',doc_type='autocompleteterm',
                body={"text":f['term'],
                    "suggest":{
                        "input":f['term'],
                        "weight":f['count']
                        }},id=id)

def facet():
    q = {
            "query" : {
                "match_all" : {  }
                },
            "facets" : {
                "text" : {
                    "terms" : {
                        "field" : "text",
                        "size" : 1000
                        }
                    }
                }
            }

    res = es.search(index='legal-index', body=q)['facets']['text']['terms']
    pp.pprint(res)
    return res


if __name__ == '__main__':
    arg = sys.argv
    if len(arg) == 3:
        locals()[arg[1]](arg[2])
    else:
        locals()[arg[1]]()
