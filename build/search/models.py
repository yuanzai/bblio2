from django.db import models

class TextFilter(models.Model):
    site = models.ForeignKey('Site')
    filter_type = models.CharField(max_length=30, db_index=True)
    filter_text = models.TextField(blank=True, null=True)
    filter_id = models.IntegerField(db_index=True, blank=True, null=True)


class Document(models.Model):
    document_text = models.TextField(blank=True, null=True, default=None)
    urlAddress = models.URLField(max_length=1000)
    domain = models.TextField()
    title = models.TextField(blank=True, null=True, default=None)
    lastupdate = models.DateTimeField(auto_now=True)
    isUsed = models.SmallIntegerField(default=0,db_index=True)
    site = models.ForeignKey('Site')
    response_code = models.SmallIntegerField(blank=True, null = True)
    document_html = models.TextField(blank=True, null = True)
    encoding = models.CharField(max_length=255, blank=True, null=True)
    update_group = models.SmallIntegerField(blank=True, null = True,db_index=True) 
    publish_date = models.DateTimeField(blank=True, null=True)
    index_batch = models.IntegerField(blank=True, null=True, db_index=True)
    head = models.ForeignKey(TextFilter,related_name='+', null=True, blank=True)
    foot = models.ForeignKey(TextFilter,related_name='+', null=True, blank=True)
    isPDF = models.BooleanField(default=False)

    def __unicode__(self):
        return self.document_text

class Site(models.Model):
    #id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=255,unique=True)
    source_allowed_domains = models.TextField()
    source_start_urls = models.TextField()
    #to decom#
    source_allowFollow = models.TextField(blank=True, null=True)
    source_denyFollow = models.TextField(blank=True, null=True)
    source_allowParse= models.TextField(blank=True, null=True)
    source_denyParse = models.TextField(blank=True, null=True)
    ##########
    parse_parameters = models.TextField(blank=True, null=True)
    follow_parameters = models.TextField(blank=True, null=True)
    deny_parameters = models.TextField(blank=True, null=True)
    lastupdate = models.DateTimeField(blank=True, null=True)
    parseCount = models.IntegerField(blank=True, null=True)
    responseCount = models.IntegerField(blank=True, null=True)
    grouping = models.CharField(max_length=255, blank=True, null=True)
    running = models.BooleanField(default=False)
    depthlimit = models.IntegerField(default=30)
    jurisdiction = models.CharField(max_length=10,blank=True,null=True)
    jobid = models.CharField(max_length=100, blank=True, null=True)
    instance = models.CharField(max_length=30, blank=True, null=True)
    owner = models.CharField(max_length=30, blank=True, null=True)

class Job(models.Model):
    scrapyd_job_id = models.CharField(max_length=100, unique=True)
    site = models.ForeignKey('Site')
    instance = models.CharField(max_length=30)

class TestingResult(models.Model):
    document = models.ForeignKey('Document')
    score = models.IntegerField()
    testinggroup = models.ForeignKey('TestingGroup')
    searchterm = models.TextField()

class TestingGroup(models.Model):
    name = models.CharField(max_length=255)

class Phrase(models.Model):
    phrase = models.TextField()
