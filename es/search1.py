#!/usr/bin/env python
import re
import pprint
from es import get_es
import sys
from search.models import Phrase
import urllib

pp = pprint.PrettyPrinter(indent=4)

def phraser(search_term):
    terms = search_term.split(' ')
    terms_count = len(terms)
    phrase_list = []
    if terms_count >1:
        for i in range(0,terms_count - 1):
            base_term = terms[i]
            for j in range(i+1,terms_count): 
                base_term = base_term + ' ' + terms[j]
                if Phrase.objects.filter(phrase=base_term).count() == 1:
                    phrase_list.append('"' + base_term + '"')
                
    pp.pprint(phrase_list)
    return phrase_list

def dequoter(search_term):
    search_term = re.sub(r'\"[^\"]+\"','""',search_term)
    pp.pprint(search_term)
    return search_term

def search(search_term,result,start_result=0):
    es = get_es()
    unquoted = dequoter(search_term).split('""')
    auto_phrases = []
    for u in unquoted:
        auto_phrases.extend(phraser(u.rstrip()))

    query_search_term = search_term
    if len(auto_phrases) > 0:
        query_search_term = search_term + ' ' + ' '.join(auto_phrases)
        pp.pprint(query_search_term)
    
    #phrase identifier
    q = {   
            "fields" : ["title","urlAddress","text"],
            "from" : start_result,
            "size" : result,
            "min_score": 0.1,
            "query": {
                "query_string": {
                    "query": query_search_term,
                                }               
                      },
            "highlight": {
                "pre_tags" : ["<b>"],
                "post_tags" : ["</b>"],
                "fields": {
                    "text": {
                        "fragment_size" : 150, 
                        "number_of_fragments": 4,
                        "no_match_size": 150,
                        "highlight_query": {
                            "query_string":{
                                "query":search_term.replace('"','')
                                }
                            }
                        }
                    }
                },
            "suggest" : {
                "text" : search_term,
                "simple_phrase" : {
                    "phrase" : {
                        "field" : "text",
                        "size" : 1,
                        "real_word_error_likelihood" : 0.95,
                        "max_errors" : 0.5,
                        "gram_size" : 2,
                        "direct_generator" : [ {
                            "field" : "text",
                            "suggest_mode" : "popular",
                            "min_word_len" : 1,
                            "min_doc_freq" : 0.01,
                            "max_term_freq" : 0.01
                            } ]                    
                        }
                    }
                }
            }

    res = es.search(index="legal-index", body=q)
    result = {}
    try:
        suggested =res['suggest']['simple_phrase'][0]['options'][0]['text'].encode('utf-8')

        result.update({'suggestion': suggested})
        result.update({'suggestion_urlencode': urllib.quote(suggested)})
        pp.pprint(urllib.urlencode(suggested))
    except:
        pass 

    r =  res['hits']['hits']
    l = []
    for re in r:
        d = {"urlAddress" : re['fields']['urlAddress'],
            #similar unicode bs
             "title" : str(re['fields']['title'][3:-2].encode('utf-8').replace("\\n",'').replace("u'","").replace("' ","").replace("\\r","").replace("',","").replace("\\t","").replace('u"','').replace('\u2019','')),


             "id" : re['_id'],
             "score" : re['_score'],}
        if d['title'] == '':
            d['title'] = d['urlAddress']
        try:
            h_list = []
            for h in re['highlight']['text']:
                #really a hacked up fix to remove rubbish terms in the highlights
                #thanks unicode not compatible python 2. thanks noob skills junyuan. thanks over encoding and ecoding of strings.
                h = h.encode('utf-8','ignore').replace("\\n",'').replace("u'","").replace("' ","")\
                        .replace("\\r","").replace("',","").replace("\\t","").replace('u"','').replace('\u2019','')
                if h[:2] in ['. ',') ',', ',"' ",")."]:
                    h = h[2:].strip()
                h_list.append(h)

            d.update({"highlight" : h_list})
        except:
            pass
        l.append(d)

    result_count = res['hits']['total']
    if not result_count:
        result_count = 0
        pp.pprint('result count zero')

    result.update({'result_list' : l})
    result.update({'result_count' : result_count})

    return result


if __name__ == '__main__':
    arg = sys.argv
    if arg[1] == 'phrase':
        phraser(arg[2])
    elif arg[1] == 'dequote':
        dequoter(arg[2])
    else:
        search(arg[1],10)
