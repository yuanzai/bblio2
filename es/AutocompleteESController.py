import json
from YTHESController import YTHESController

class AutocompleteESController(YTHESController):

    _es_autocomplete_index = "autocomplete-index"

    def get_autocomplete(self, search_term):
        s = {
                "text-suggest" : {
                    "text" : search_term,
                    "completion" : {
                        "field" : "suggest"
                    }
                }
            }
    res = self._es.suggest(index=self._es_autocomplete_index,body=s)
    result = []
    for r in res['text-suggest'][0]['options']:
        r_dict = {
                "id": r['text'].encode('utf-8'),
                "label": r['text'].encode('utf-8'),
                "value": r['text'].encode('utf-8')
                }
        result.append(r_dict)
    return json.dumps(result)

    def index_autocomplete(self):      
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
        self.delete_autocomplete()
        self._es.indices.create(index=self._es_autocomplete_index,body=s)
        for id, f in enumerate(term_facet_list()):
            es.index(index='autocomplete',doc_type='autocompleteterm',
                    body={"text":f['term'],
                        "suggest":{
                            "input":f['term'],
                            "weight":f['count']
                            }},id=id)

    def term_facet_list(self):
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
        if not self._es_index:
            raise AutocompleteESControllerError("Index not defined")
        res = es.search(index=self._es_index, body=q)['facets']['text']['terms']
        return res
 
