from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.core.urlresolvers import reverse
import httplib
import threading
import json
import time
import urllib2


def index(request):

    return render(request, 'emplifive/index.html')

