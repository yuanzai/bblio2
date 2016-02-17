import boto.ec2
import keys
import sys
from ec2 import getCrawlerInstances, getCrawlerInstance
from boto.manage.cmdshell import sshclient_from_instance
import os
import fnmatch
import httplib, urllib

home_dir = '/home/ec2-user/bblio/'

def curl(method, params=None):
    params = urllib.urlencode(
            {
                'project': 'default', 
                'spider': 'SpiderSolo', 
                })
    headers = {
            "Content-type": "application/x-www-form-urlencoded",
            "Accept": "text/plain"}
    
    conn = httplib.HTTPConnection("54.187.248.155", port=6800)
    conn.request("POST", "/schedule.json", params, headers)
    response = conn.getresponse()
    print response.status, response.reason
    data = response.read()
    print data
    conn.close()
    return data

def curl_add():
    params = urllib.urlencode({'project': 'default', 'spider': 'SoloSpider', 'id':23})
    curl("/schedule.json",params)

def get_ssh_client():
    #return sshclient_from_instance(getCrawlerInstance(), host_key_file = '/home/ec2-user/.ssh/known_hosts', ssh_key_file='',user_name='ec2-user')
    return sshclient_from_instance(getCrawlerInstance(), host_key_file = '/home/ec2-user/.ssh/known_hosts', ssh_key_file=keys.aws_pem,user_name='ec2-user')

def get_ssh_client_list():
    return [sshclient_from_instance(i, host_key_file = '/home/ec2-user/.ssh/known_hosts', ssh_key_file=keys.aws_pem,user_name='ec2-user') for i in getCrawlerInstances()]
    #return [sshclient_from_instance(i, host_key_file = '/home/ec2-user/.ssh/known_hosts', ssh_key_file='',user_name='ec2-user') for i in getCrawlerInstances()]

def process_crawl(site_id):
    get_ssh_client().run('python2.7 ' + home_dir + 'scraper/scrapeController.py ' + str(site_id))

def crawl_site_id(site_id):
    import threading
    t = threading.Thread(target=process_crawl,args=(site_id,))
    t.setDaemon(True)
    t.start()

def clear_schedule(site_id):
    status, stdin, stderr = get_ssh_client().run('python2.7 ' + home_dir + 'scraper/scrapeController.py clear ' + str(site_id))

def copy_files():
    copyList = []   
    copyList.append(home_dir + 'build/search/models.py')
    copyList.append(home_dir + 'build/search/__init__.py')
    copyList.append(home_dir + 'build/Build/__init__.py')
    copyList.append(home_dir + 'build/Build/settings.py.crawler')
    copyList.append(home_dir + 'build/Build/apps.py.crawler')
    copyList.append(home_dir + 'build/Build/myScript.py.crawler')
    copyList.append(home_dir + 'build/manage.py')
    copyList.append(home_dir + 'build/__init__.py')
    copyList.append(home_dir + 'aws/ec2.py')
    copyList.append(home_dir + 'aws/keys.py')
    copyList.append(home_dir + 'aws/key.pem')
    copyList.append(home_dir + 'aws/__init__.py')
    copyList.append(home_dir + 'bblio.cfg')
    copyList.append(home_dir + 'config_file.py')
    copyList.append(home_dir + '__init__.py')
    copyList.append(home_dir + 'scrapyd.conf')
    for root, dirnames, filenames in os.walk(home_dir + 'scraper'):
        for filename in fnmatch.filter(filenames, '*.py'):
            copyList.append(os.path.join(root, filename))
        for filename in fnmatch.filter(filenames, '*.cfg'):
            copyList.append(os.path.join(root, filename))
    ssh_clients = get_ssh_client_list()
    dirList = []
    for c in copyList:
        c_dir = os.path.dirname(c)
        prev_dir = ''
        while c_dir != prev_dir and c_dir not in home_dir:
            if c_dir not in dirList:
                dirList.append(c_dir)
            prev_dir = c_dir
            c_dir = os.path.dirname(c_dir)
    dirList.append(home_dir) 
    dirList.sort(lambda x,y: cmp(len(x), len(y)))
    if len(ssh_clients) == 0:
        print "No ssh clients"
    
    if ssh_clients == None:
        print "No ssh clients"

    for d in dirList:
        for s in ssh_clients:
            print('[dir][%s] %s' % (s.server.hostname, d))
            s.run('mkdir %s' % d)

    for c in copyList:
        for s in ssh_clients:
            print('[file][%s] %s' % (s.server.hostname, c))
            s.put_file(c,c.replace('.crawler',''))


if __name__ == '__main__':
    arg = sys.argv
    if len(sys.argv) > 1:
        if arg[1] == 'copy':
            copy_files()
        elif arg[1] == 'curl':
            curl_add()


