#base class import
from BaseESController import BaseESController

#pdf import
from PDFController import PDFController

#python imports
import re
from lxml import etree
from lxml.html.clean import clean_html

from io import StringIO, BytesIO
import sys 
import cgi

#django imports
from search.models import Site, Document, TextFilter

#TemplateTerms
from TemplateTerms import TemplateTerms

class YTHESController(BaseESController):
    _es_index = "yth-index"
    _doc_type = "yth-doc"
    _xpath =  "body/descendant-or-self::*[not(self::script|self::link|self::code|self::option|self::header|self::nav)]"

    def search_raw_result(self, search_term, jurisdiction = [],
            results_per_page=10,
            current_page=1):
        query = {}
        
        #searching component
        
        q = {
                #fields to return in the ES request
                "fields" : ["title","text","urlAddress"], 

                #start result - from 0
                "from" : (int(current_page) - 1) * results_per_page,
                "size" : results_per_page,
                "min_score": 0.1,
                "query": {
                    "query_string": {
                        "default_field" : "text",
                        "query": search_term,
                                    }
                          }
                }
        query.update(q)

        #highlights - ie the summarised data in the search result
        h = {
                "pre_tags" : ["<b>"],
                "post_tags" : ["</b>"],
                "fields": {
                    "text": {
                        "type" : "plain",
                        #"fragment_size" : 100,
                        #"number_of_fragments": 3,
                        #"no_match_size": 100,
                        #"highlight_query": {
                        #   "query_string":{
                        #        "default_field" : "text",
                        #        "query":search_term.replace('"','')
                        #    }
                        #}
                    }
                }
            }
        query.update({"highlight" : h})
        
        #suggestion - ie did you mean
        s = {
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

        query.update({"suggest" : s})

        #filters - currently for jurisdiction as of now
        f = {
                "term": {
                    "jurisdiction": jurisdiction
                }
            }
        if jurisdiction: query.update({"filter" : f })
        return self._es.search(index=self._es_index, body=query)
    
    def search(self, search_term, jurisdiction = [],
            results_per_page=10,
            current_page=1):

        res = self.search_raw_result(search_term,jurisdiction , results_per_page, current_page)
        print res
        result = {}
        """
        takes the raw return from elastic search and handles the suggestions
        """
        try:
            suggested =res['suggest']['simple_phrase'][0] \
                    ['options'][0]['text'].encode('utf-8')
            
            #suggestion
            result.update({'suggestion': suggested})

            #suggestion URL
            result.update({'suggestion_urlencode': urllib.quote(suggested)})
        except:
            pass

        """
        takes the raw return from ES and handles the hit results and highlights
        """
        l = []
        for re in res['hits']['hits']:
            d = {"urlAddress" : re['fields']['urlAddress'],
                 "id" : re['_id'],
                 "score" : re['_score'],}
           
            try:
                d.update({"title": re['fields']['title']})
            except:
                d.update({"title": d['urlAddress']})

            try:
                h_list = []
                for h in re['highlight']['text']:
                    h_list.append(h)

                d.update({"highlight" : h_list})
            except:
                pass
            l.append(d)

        """
        total count
        """

        result_count = res['hits']['total']
        if not result_count:
            result_count = 0

        result.update({'result_list' : l})
        result.update({'result_count' : result_count})

        return result

    def index_one_doc(self, Document):
        if not self._es.indices.exists(index=self._es_index):
            self._es.indices.create(index=self._es_index,body=self.get_mapping())
         
        doc = self.get_doc(Document)
        if not doc:
            pass
        else:
            return self._es.index(
                index=self._es_index,
                doc_type=self._doc_type,
                body=doc,
                id=Document.id)

    def index_all_html(self, index_batch=None):
        i = 0
        e = 0
        site_list = Site.objects.filter(grouping__in=['works','works dirty']).filter(isPDF=True).values_list('id',flat=True)
        for s in site_list:
            print 'site ' + str(s)
            doc_list = Document.objects.filter(site_id=s).filter(isUsed=0).exclude(encoding='PDF').values_list('id',flat=True)
            for d in doc_list:
                doc = Document.objects.get(pk=d)
                if index_batch:
                    if doc.index_batch >= index_batch:
                        continue
                try:
                    res = self.index_one_doc(doc)
                    if res['ok']:
                        doc.index_batch=index_batch
                        doc.save()
                    i += 1
                except:
                    e += 1
                finally:
                    doc = None
                if i % 1000 == 0 and i >0:
                    print 'indexed ' + str(i)
            s = None

            print 'indexed ' + str(i)
            print 'errored ' + str(e)

    def delete_non_zeroes(self):
        doc_list = Document.objects.exclude(isUsed=0).exclude(encoding='PDF').values_list('id',flat=True)
        for d in doc_list:
            try:
                print 'delete ' + str(d)
                self.delete_one_doc(d)
            except:
                pass

    def get_doc(self, Document):
        site = Site.objects.get(pk=Document.site_id)
        doc = {
                "urlAddress" : Document.urlAddress,
                "jurisdiction" : site.jurisdiction,
                "site_id" : site.id
        }
 
        if Document.encoding == 'PDF':
            pdf = PDFController()
            
            try:
                doc.update({
                    "title" : Document.urlAddress,
                    "text" : pdf.get_string_from_s3_key(Document.urlAddress),
                    })
            except:
                return None
        else:
            doc.update({
                "title" : self.title_parse(Document.document_html),
                "text" : self.text_parse(Document),
                })
        return doc
    
    def get_tree(self, text):
        text = re.sub('<strong>','',text)
        text = re.sub('</strong>','',text)
        text = re.sub('\n','',text)
        text = re.sub('\t','',text)
        text = re.sub(r'\s+',' ',text)
        text = re.sub('\<\?xml version\=\"1.0\" encoding\=\"UTF-8\"\?\>', '',text)
        
        parser = etree.HTMLParser(recover=True, encoding ='utf-8', remove_comments=True, remove_blank_text=True,remove_pis=True)
        #tree = etree.parse(StringIO(text.encode('utf-8').decode('utf-8')), parser)
        tree = etree.parse(StringIO(text), parser)

        return tree

    def get_body_html(self, text):
        tree = self.get_tree(text)
        result = tree.xpath(self._xpath)
        body = []
        for s in result:
            body.append(etree.tostring(s))
        return '\n'.join(body)

    def title_parse(self, text):
        tree = self.get_tree(text)
        try:
            return tree.xpath("//title/text()")[0]
        except:
            return

    def text_parse(self, Document, delimiter = ' '):
        doc_text =  delimiter.join([t for t in self.text_array(Document) if t !=''])
        
        if TextFilter.objects.filter(site_id=Document.site_id).filter(filter_type='head').count() == 1:
            f = TextFilter.objects.filter(site_id=Document.site_id).filter(filter_type='head')
            doc_text = doc_text[len(f[0].filter_text):]
        
        if TextFilter.objects.filter(site_id=Document.site_id).filter(filter_type='foot').count() == 1:
            f = TextFilter.objects.filter(site_id=Document.site_id).filter(filter_type='foot')
            doc_text = doc_text[:-len(f[0].filter_text)]

        return doc_text

    def text_array(self, Document):
        tree = self.get_tree(Document.document_html)
        result = tree.xpath(self._xpath + "/text()")
        ban_list = ['">']
        for r in tree.xpath(self._xpath):
            try:
                if r.text.strip() in ban_list:
                    r.getparent().remove(r)
            except:
                pass
        
        result = tree.xpath(self._xpath + "/text()")
        return [t for t in result if (t.strip() !='' and len(t.strip()) >1)]
        



    def get_mapping(self):
        m = {
                "mappings":{
                    self._doc_type:{
                        "properties":{
                            "text":{
                                "type":"string",
                                "analyzer":"my_analyzer"
                                },
                            "jurisdiction":{
                                "type" : "string",
                                "index" : "not_analyzed"
                                },
                            "site_id":{
                                "type" : "long",
                                "index" : "not_analyzed"
                                }
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

if __name__ == '__main__':
    arg = sys.argv
    if len(sys.argv) > 1:
        es = YTHESController()
        getattr(es, arg[1])()

