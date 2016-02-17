from django import template
from es.YTHESController import YTHESController as ESController
from search.models import Document
import aws.ec2

register = template.Library()

#navbar renders
@register.inclusion_tag('operations/operations_navbar.html')
def navbar_inclusion():
    es = ESController()    
    instance_ips = [{'url':i.ip_address,'name':i.id} for i in aws.ec2.getCrawlerInstances()]
    return {"es_count":es.get_document_count(), 'crawlers':instance_ips, 'zero_count' : Document.objects.filter(isUsed=0).count()}
