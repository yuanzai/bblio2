#!/usr/bin/env python
import pprint
from es import get_es
import sys
pp = pprint.PrettyPrinter(indent=4)

def facet():
    es = get_es()
    q = {
            "query" : {
                "match_all" : {  }
                },
            "facets" : {
                "text" : {
                    "terms" : {
                        "field" : "text",
                        "size" : 100
                        }
                    }
                }
            }

    res = es.search(index='legal-index', body=q)['facets']
    pp.pprint(res)
    return res

if __name__ == '__main__':
    arg = sys.argv
    locals()[arg[1]]()
