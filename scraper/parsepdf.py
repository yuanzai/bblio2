from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfpage import PDFTextExtractionNotAllowed
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams



fp = open('/home/ec2-user/bblio/scraper/pdf/test.pdf', 'rb')
parser = PDFParser(fp)
document = PDFDocument(parser)
if not document.is_extractable:
    raise PDFTextExtractionNotAllowed
else:
    print 'win'

rsrcmgr = PDFResourceManager()
outfp = file('/home/ec2-user/bblio/scraper/pdf/test.txt', 'w')

laparams = LAParams()
device = TextConverter(rsrcmgr, outfp, codec='utf-8', laparams=laparams)

interpreter = PDFPageInterpreter(rsrcmgr, device)
for page in PDFPage.get_pages(fp, set()):
    #page.rotate = (page.rotate+rotation) % 360
    interpreter.process_page(page)
fp.close()
device.close()
outfp.close()

