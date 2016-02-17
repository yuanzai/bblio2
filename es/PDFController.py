from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfpage import PDFTextExtractionNotAllowed
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from cStringIO import StringIO
from aws.ec2 import retrieve_file_from_S3
import random
import string
import os
class PDFController(object):
    def __init__(self):
        pass
    
    def get_string_from_s3_key(self,key):
        temp_name = "/home/ec2-user/bblio/scraper/pdf/temp" + ''.join([random.choice(string.ascii_letters + string.digits) for n in xrange(32)]) + ".pdf" 
        retrieve_file_from_S3(key, temp_name)
        ret = self.get_string(temp_name)
        os.remove(temp_name)
        return ret

    def get_string(self, pdf_path):
        
        fp = open(pdf_path, 'rb')
        parser = PDFParser(fp)
        document = PDFDocument(parser)
        if not document.is_extractable:
            raise PDFTextExtractionNotAllowed

        rsrcmgr = PDFResourceManager()
        outfp = StringIO()
        
        laparams = LAParams()
        device = TextConverter(rsrcmgr, outfp, codec='utf-8', laparams=laparams)

        interpreter = PDFPageInterpreter(rsrcmgr, device)
        for page in PDFPage.get_pages(fp, set()):
            interpreter.process_page(page)
        fp.close()
        device.close()
        ret = outfp.getvalue()
        outfp.close()
        return ret
