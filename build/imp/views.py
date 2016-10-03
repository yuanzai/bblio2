from django.shortcuts import render, get_object_or_404

from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.core.urlresolvers import reverse
import httplib, urllib



def main(request):
    conn = httplib.HTTPSConnection("agent.electricimp.com")
    conn.request("GET", "/UppHuN5QWabW?name=AndroidAP")
    response = conn.getresponse()
    print response.status, response.reason    data = response.read()
    print data
    conn.close()
    return HttpResponse("Hello")
