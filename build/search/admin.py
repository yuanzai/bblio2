from django.contrib import admin
from models import Site
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from models import Document
import views
import sys
sys.path.append('/home/ec2-user/bblio/es/')
import es

class SiteAdmin(admin.ModelAdmin):
    def run_deny_filter(modeladmin, request, queryset):
        for q in queryset:
            docs = Document.objects.filter(site=q)
            if source_denyParse:
                denys = q.source_denyParse.split(';')
                for deny in denys:
                    d = docs.filter(urlAddress__contains=deny)
                    d.update(isUsed=1)

    def run_dupe_filter(modeladmin, request, queryset):
        for q in queryset:
            docs = Document.objects.filter(site=q)
            urlList = docs.values_list('urlAddress',flat=True).distinct()
            #import pdb; pdb.set_trace()
            for url in urlList:
                d = docs.filter(urlAddress=url)
                if len(d) > 1:
                    first_id = docs.filter(urlAddress=url)[0].id
                    d.exclude(pk=first_id).update(isUsed=2)

    def run_http_s_filter(modeladmin, request, queryset):
        for q in queryset:
            docs = Document.objects.filter(site=q)
            urlList = docs.values_list('urlAddress',flat=True).distinct()
            for url in urlList:
                if url[:5] == 'https':
                    url2 = url[:4] + url[5:]
                    if len(docs.filter(urlAddress=url2)) > 0:
                        docs.filter(urlAddress=url).update(isUsed=3)

    def run_www_dupe_filter(modeladmin, request, queryset):
        for q in queryset:
            docs = Document.objects.filter(site=q)
            urlList = docs.values_list('urlAddress',flat=True).distinct()
            for url in urlList:
                if url[:11] == 'https://www':
                    url2 = 'https://' + url[12:]
                elif url[:10] == 'http://www':
                    url2 = 'http://' + url[11:]
                else:
                    url2 = None

                if url2:
                    d = docs.filter(urlAddress=url2)
                    if len(d) > 0:
                        d.update(isUsed=4)


    def run_es_clean(modeladmin, request, queryset):
        for q in queryset:
            docs = Document.objects.filter(site=q).filter(isUsed__gt=0).values_list('id',flat=True)
            for d in docs:
                try:
                    es.delete(d)
                except:
                    print(d)

    def run_slash_dupe_filter(modeladmin, request, queryset):
        for q in queryset:
             docs = Document.objects.filter(site=q)
             urlList = docs.values_list('urlAddress',flat=True).distinct()
             for url in urlList:
                 if url[1:] == '/':
                     url2 = url[:-1]
                     if len(docs.filter(urlAddress=url2)) > 0:
                         docs.filter(urlAddress=url).update(isUsed=5)



    list_display = ('name','id','grouping','depthlimit','show_current_doc_count','parseCount','responseCount','lastupdate','show_urls_parsed','delete_doc',)
    # fields = ('name','grouping','source_allowed_domains','source_start_urls','source_allowParse','source_denyParse','source_allowFollow','source_denyFollow')
    list_editable = ('grouping','depthlimit',)
    ordering = ('id',)
    exclude = ('id','lastupdate','parseCount','responseCount')
    readonly_fields = ('id',)

    list_per_page = 200
    actions = ['run_deny_filter','run_dupe_filter','run_http_s_filter','run_www_dupe_filter','run_es_clean','run_slash_dupe_filter']
    run_dupe_filter.short_description = 'Set document isUsed to 2 via dupe filter'
    run_deny_filter.short_description = 'Set document isUsed to 1 via deny parse'
    run_http_s_filter.short_description = 'Set document isUsed to 3 via https filter'
    run_www_dupe_filter.short_description = 'Set document isUsed to 4 via www dupe filter'
    run_es_clean.short_description = 'Remove from ES index'

    def show_current_doc_count(self, obj):
        return Document.objects.filter(site=obj).filter(isUsed=0).count()
    show_current_doc_count.short_description = 'Doc Count'

    def show_urls_parsed(self, obj):
        return '<a href="%s">%s</a>' % (reverse('search.views.scraped', args=(str(obj.id),)), 'URL List')
    show_urls_parsed.allow_tags = True
    show_urls_parsed.short_description = 'Parsed URLs'

    def delete_doc(self, obj):
        return '<a href="%s">%s</a>' % (reverse('search.views.delete', args=(str(obj.id),)), 'Delete docs')
    delete_doc.allow_tags = True


admin.site.register(Site,SiteAdmin)

