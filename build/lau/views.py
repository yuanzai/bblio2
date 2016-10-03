from django.shortcuts import render, get_object_or_404

from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.core.urlresolvers import reverse
import httplib
import threading
import json
import time
import urllib2
from shutil import copyfile
import trilateration


# hard coded imp locations and the respective agent urls
devices = [
            {'name' : 'a',
             'url' :'UppHuN5QWabW',
             'x' : 24,
             'y' : 30},
            {'name' : 'b',
             'url' : 'FW9ok9HTkzDn',
             'x' : 2,
             'y' : 62}, 
            {'name':'m',
             'url' : 'WlrU3EmK0FJu',
             'x' : 46,
             'y' : 62}
           ]
imp_site = "https://agent.electricimp.com/"

def index(request):
    return render(request, 'lau/index.html')

def imp(request):
    """
    This is the method that is kicked off when the mobile phone makes a request to the web server
    """

    if 'hotspot' in request.GET:
        # Obtains the hotspot name of the mobile phone
        # and starts method that begins a multithreaded request for the signal strengths
        #result = launch_threads(request.GET['hotspot'])
        result = {}
        result.update({'a':{'signal':-44},'b':{'signal':-42},'m':{'signal':-41}})
         
        # converts signal strength from the imp to a pysical distance
        # conversion is done through a method defined below
        d1 = process_signal(result[devices[0]['name']]['signal'])
        d2 = process_signal(result[devices[1]['name']]['signal'])
        d3 = process_signal(result[devices[2]['name']]['signal'])
        
        # using a graphing library, the 3 imp location and distances are plotted on a graph and
        # exported to a png file
        img_src = trilateration.trilaterate(devices[0]['x'],devices[0]['y'],d1,
                devices[1]['x'],devices[1]['y'], d2,
                devices[2]['x'],devices[2]['y'],d3)

        # relevant html code to print the data
        string = "<ul><li>"+str(devices[0]) + " " + str(result[devices[0]['name']]) + "</li>"
        string = string + "<li>"+str(devices[1]) + " " + str(result[devices[1]['name']]) + "</li>"
        string = string + "<li>"+str(devices[2]) + " " + str(result[devices[2]['name']]) + "</li></ul>"

        # html code to show image
        return HttpResponse(string + "<img src='http://jy-lau.me/static/"+img_src+"'>")

def process_signal(x):
    # simple method to convert signal to distance
    # conversion is based on real world testing done by me
    if x > -20:
        return 5
    elif x < -20 and x >= -30:
        return -(x - (-20)) * 0.5 + 5
    elif x < -30 and x >= -40:
        return -(x - (-30)) + 10
    elif x < -40 :
        return -(x - (-40)) * 3 + 20


def launch_threads(hotspot_name):
    # method to launch threads to send requests to agent
    result = {}
    result.clear()
    for d in devices:
        thr = threading.Thread(target=get_data, args=(d, hotspot_name, result)).start()
    t = 0
    while t < 15 and len(result) < len(devices):
        time.sleep(1)
        t += 1
    return result


def get_data(device, hotspot_name, result):
    #individual URL calls
    url = imp_site + device['url'] + '?name=' + hotspot_name
    urlHandler = urllib2.urlopen(url)
    html = urlHandler.read()
    data = json.loads(html)
    result.update({device['name'] : { 'signal' : data['d']}})
    return json.loads(html)

