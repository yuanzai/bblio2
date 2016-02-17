import boto
import keys
from boto.s3.key import Key


conn = boto.connect_s3(keys.aws_access_key_id, keys.aws_secret_access_key)
b = conn.get_bucket("bblio")

k = Key(b)

k.key = 'test.txt'
k.set_contents_from_filename(k.key)


