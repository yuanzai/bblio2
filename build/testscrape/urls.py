from django.conf.urls import url
from django.http import HttpResponse
from django.core.urlresolvers import reverse

# def home():
#     return reverse('testscrape.urls.index')


def index(request):
    return HttpResponse("""
            <a href="follow">follow</a><br>
            <a href="parse">parse</a><br>
            <a href="deny">deny</a><br>
            <a href="slow">slow</a><br>
            <a href="forever">forever ie 10 min</a><br>
            <a href="date/2000/10/10/">date</a><br>
            <a href="date/2000/01/28/">date2</a><br>
            <a href="date/2000/10/this_is_LitigoSearch">year/month/article-title</a><br>
            <a href="/static/pdf-sample.pdf">PDF</a><br>
            <a href="t1_L1">[L1] Type 1 - Never-ending Blog (fine, it ends at the maiden post)</a><br>
            <a href="t2_L1">[L1] Type 2 - Firm's Site / Archives</a><br>
            <a href="t3_L1">[L1] Type 3 - Firm's Site: Several Articles on Each Page</a>
            <a href="http://www.quora.com/">This is QUORA!!</a>
            """)


# test for Type 1 sites
def t0_FB(request):
    return HttpResponse('This is a FB page we do not want to parse. Ever.')


def t1_L1(request):
    return HttpResponse("""
        <a href="/testscrape/t1_L2">[L2] Previous Article</a><br>
        <a href="/testscrape/t0_www.facebook.com">[L2] Lame FB Link</a><br>
        """)

def t1_L2(request):
    return HttpResponse("""
        <a href="/testscrape/t1_L3">[L3] Previous Article</a><br>
        <a href="/testscrape/t1_L1">[L3] Newer Article</a><br>
        <a href="/testscrape/t0_www.facebook.com">[L3] Lame FB Link</a><br>
        """)

def t1_L3(request):
    return HttpResponse("""
        <a href="/testscrape/t1_L4">[L4] Previous Article</a><br>
        <a href="/testscrape/t1_L2">[L4] Newer Article</a><br>
        <a href="/testscrape/t0_www.facebook.com">[L4] Lame FB Link</a><br>
        """)

def t1_L4(request):
    return HttpResponse("""
        This is the oldest article on this blog. Can't go beyond this!<br>
        <a href="/testscrape/t1_L3">[L5] Newer Article</a><br>
        """)


# test for Type 2 sites
def t2_L1(request):
   return HttpResponse("""
       <a href="/testscrape/t2_L2a">[L2] Barrister A</a><br>
       <a href="/testscrape/t2_L2b">[L2] Barrister B</a><br>
       <a href="/testscrape/t2_L2c">[L2] Barrister C</a><br>
       """)

def t2_L2a(request):
   return HttpResponse("""
       <a href="/testscrape/t2_L3a">[L2] Barrister A's Commentaries<br>
       <a href="/testscrape/t0_www.facebook.com">[L2] These links should NOT be parsed.</a><br>
       """)

def t2_L2b(request):
   return HttpResponse("""
       <a href="/testscrape/t2_L3b">[L2] Barrister B's Commentaries<br>
       <a href="/testscrape/t0_www.facebook.com">[L2] These links should NOT be parsed.</a><br>
       """)

def t2_L2c(request):
   return HttpResponse("""
       <a href="/testscrape/t2_L3c">[L2] Barrister C's Commentaries<br>
       <a href="/testscrape/t0_www.facebook.com">[L2] These links should NOT be parsed.</a><br>
       """)

def t2_L3a(request):
    return HttpResponse('Blah Blah Blah by Barrister A and there exists no damn link to take me back up by 1 lvl')

def t2_L3b(request):
    return HttpResponse('Blah Blah Blah by Barrister B and there exists no damn link to take me back up by 1 lvl')

def t2_L3c(request):
    return HttpResponse('Blah Blah Blah by Barrister C and there exists no damn link to take me back up by 1 lvl')


# test for Type 3 sites
def t3_L1(request):
    return HttpResponse("""
        <a href="/testscrape/t3_L2a1">[L2] Article 1</a><br>
        <a href="/testscrape/t3_L2a2">[L2] Article 2</a><br>
        <a href="/testscrape/t3_L2a3">[L2] Article 3</a><br>
        <a href="/testscrape/t3_L2p2">[L2] Page 2</a><br>
        <a href="/testscrape/t3_L2p3">[L2] Page 3</a>
        """)

def t3_L2a1(request):
    return HttpResponse("""
        This is Article 1 and it is a really boring article..
        """)

def t3_L2a2(request):
    return HttpResponse("""
        This is Article 2 and it is an 'okay' article..
        """)

def t3_L2a3(request):
    return HttpResponse("""
        This is Article 3 and it is a really useful article!
            """)

def t3_L2p2(request):
    return HttpResponse("""
        <a href="/testscrape/t3_L2a4">[L3] Article 4</a><br>
        <a href="/testscrape/t3_L2a5">[L3] Article 5</a><br>
        <a href="/testscrape/t3_L2a6">[L3] Article 6</a><br>
        <a href="/testscrape/t3_L2p3">[L3] Page 3</a><br>
        <a href="/testscrape/t3_L2p4">[L3] Page 4</a>
        """)

def t3_L2p3(request):
    return HttpResponse("""
        <u>Article 7</u><br>
        <u>Article 8</u><br>
        <u>Article 9</u>
        """)

def t3_L2(request):
    return HttpResponse("""
        <a href="/testscrape/t3_L2a4">[L3] Article 4</a><br>
        <a href="/testscrape/t3_L2a5">[L3] Article 5</a><br>
        <a href="/testscrape/t3_L2a6">[L3] Article 6</a><br>
        <a href="/testscrape/t3_L2p3">[L3] Page 3</a><br>
        <a href="/testscrape/t3_L2p4">[L3] Page 4</a>
        """)

def t3_L2a4(request):
    return HttpResponse('This is Article 4 and it is a really boring article..')

def t3_L2a5(request):
    return HttpResponse('This is Article 5 and it is a really useful article!')

def t3_L2a6(request):
    return HttpResponse("""
        This is Article 6 and it is a really useful article!
        """)

def t3_L2p4(request):
    return HttpResponse("""
        <u>Article 10</u><br>
        <u>Article 11</u><br>
        <u>Article 12</u>
        """)

# originals by JY
def uk(request):
    return HttpResponse('<a href="2">UK2</a>')

def uk2(request):
    return HttpResponse('UK2')

def follow(request):
    return HttpResponse('Followed Link')

def parse(request):
    return HttpResponse('Parsed Link')

def deny(request):
    return HttpResponse('Denied Link')

def slow(request):
    import time
    time.sleep(30)
    return HttpResponse('Slow link')

def forever(request):
    import time
    time.sleep(600)
    return HttpResponse('Forever link')

def date(request):
    return HttpResponse('Date link')


urlpatterns = [
    url(r'^$', index),
    url(r'^follow/$', follow),
    url(r'^parse/$', parse),
    url(r'^deny/$', deny),
    url(r'^slow/$', slow),
    url(r'^forever/$',forever),
    url(r'^uk/$',uk),
    url(r'^uk/2/$',uk2),
    url(r'^date/\d{4}/\d{2}/\d{2}/$', date),
    url(r'^t0_www.facebook.com/$', t0_FB),
    url(r'^t1_L1/$', t1_L1),
    url(r'^t1_L2/$', t1_L2),
    url(r'^t1_L3/$', t1_L3),
    url(r'^t1_L4/$', t1_L4),
    url(r'^t2_L1/$', t2_L1),
    url(r'^t2_L2a/$', t2_L2a),
    url(r'^t2_L2b/$', t2_L2b),
    url(r'^t2_L2c/$', t2_L2c),
    url(r'^t2_L3a/$', t2_L3a),
    url(r'^t2_L3b/$', t2_L3b),
    url(r'^t2_L3c/$', t2_L3c),
    url(r'^t3_L1/$', t3_L1),
    url(r'^t3_L2a1/$', t3_L2a1),
    url(r'^t3_L2a2/$', t3_L2a2),
    url(r'^t3_L2a3/$', t3_L2a3),
    url(r'^t3_L2p2/$', t3_L2p2),
    url(r'^t3_L2p3/$', t3_L2p3),
    url(r'^t3_L2a4/$', t3_L2a4),
    url(r'^t3_L2a5/$', t3_L2a5),
    url(r'^t3_L2a6/$', t3_L2a6),
    url(r'^t3_L2p3/$', t3_L2p3),
    url(r'^t3_L2p4/$', t3_L2p4),
    ]
