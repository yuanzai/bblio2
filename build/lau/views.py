from django.shortcuts import render, get_object_or_404

from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.core.urlresolvers import reverse

def index(request):
    return render(request, 'lau/index.html')
