from __future__ import unicode_literals

from django.apps import AppConfig
import sys

path = "/home/ec2-user/bblio/"
if path not in sys.path:
    sys.path.append(path)

class BuildConfig(AppConfig):
    name = 'Build'

class SearchConfig(AppConfig):
    name = 'search'

class OperationsConfig(AppConfig):
    name = 'operations'

class ScraperConfig(AppConfig):
    name = 'scraper'

class LauConfig(AppConfig):
    name = 'lau'
