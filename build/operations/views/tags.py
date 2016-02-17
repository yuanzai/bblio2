from django import template
from es.YTHESController import YTHESController as ESController

register = template.Library()

#navbar renders
@register.inclusion_tag('operations/operations_navbar.html')
def navbar_inclusion():
    #es = ESController()
    print 'hello'
    return {"es_count": "6"}
