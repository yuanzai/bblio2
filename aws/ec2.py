import boto.ec2
import boto.s3
from boto.s3.key import Key
import sys
sys.path.append('/home/ec2-user/bblio/')
from boto.manage.cmdshell import sshclient_from_instance
import keys
from config_file import get_config
import os

def conn():
    return boto.ec2.connect_to_region("us-west-2",
        aws_access_key_id=keys.aws_access_key_id,
        aws_secret_access_key=keys.aws_secret_access_key)

def testConn():
    c = boto.ec2.connect_to_region("us-west-2", aws_access_key_id=keys.aws_access_key_id, aws_secret_access_key=keys.aws_secret_access_key)
    print c.get_all_instances()
    
    
    
def startES():
    conn().start_instances(instance_ids=get_config().get('bblio','es_instance'))

def stopES():
    conn().stop_instances(instance_ids=get_config().get('bblio','es_instance'))

def getInstance(instance_name, attr=None):
    try:
        instance = conn().get_only_instances(instance_name)[0]
    except:
        return None

    if attr:
        try:
            instanceA = getattr(instance, attr)
            return instanceA
        except AttributeError:
            pass
    return instance

def getWebServerIP():
    return getInstance(get_config().get('bblio','web_server_instance'),'dns_name')

def getWebServerInstance():
    return 'localhost'
    #return getInstance(get_config().get('bblio','web_server_instance'))

def getESip():
    return getInstance(get_config().get('bblio','es_instance'),'dns_name')

def getCrawlerIP():
    return conn().get_all_instances(instance_ids=get_config().get('bblio','crawler_instance'))[0].instances[0].dns_name

def getInstanceFromInstanceName(instance_name):
    return conn().get_all_instances(instance_ids=instance_name)[0].instances[0]

def getCrawlerInstance():
    return conn().get_all_instances(instance_ids=get_config().get('bblio','crawler_instance').split(';')[0])[0].instances[0]

def getCrawlerInstances():
    crawler_list = []
    for c in [getInstance(i) for i in get_config().get('bblio','crawler_instance').split(';')]:
        if c == None:
            continue
        try:
            if c.ip_address:
                crawler_list.append(c)
        except AttributeError:
            pass
       

    return crawler_list 

def copy_file_to_web_server(local_filepath,web_server_filepath):
    ssh_client = sshclient_from_instance(getWebServerInstance(),host_key_file = '/home/ec2-user/.ssh/known_hosts', ssh_key_file=keys.aws_pem,user_name='ec2-user')
    ssh_client.put_file(local_filepath, web_server_filepath)

def copy_file_to_S3(s3_key, local_filename):
    conn = boto.connect_s3(keys.aws_access_key_id, keys.aws_secret_access_key)
    b = conn.get_bucket('bblio')
    k = Key(b)
    k.key = s3_key
    ret = k.set_contents_from_filename(local_filename)
    if ret > 0:
        return True
    else:
        return False

def retrieve_file_from_S3(s3_key, save_path):
    conn = boto.connect_s3(keys.aws_access_key_id, keys.aws_secret_access_key)
    b = conn.get_bucket('bblio')
    k = Key(b)
    k.key = s3_key
    k.get_contents_to_filename(save_path)

if __name__ == '__main__':
        arg = sys.argv    
        if len(sys.argv) > 1:
            if arg[1] == 'crawlers':
                for i in getCrawlerInstances():
                    print i.id
                    print i.ip_address
            elif arg[1] == 'test':
                testConn()


