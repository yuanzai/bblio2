import unittest
import sys
sys.path.append('/home/ec2-user/bblio/es/')
sys.path.append('/home/ec2-user/bblio/build/')

from YTHESController import YTHESController
from search.models import Document

class TestBaseESController(unittest.TestCase):

    def setUp(self):
        self.testcontroller = YTHESController()

    def test_object(self):
        self.assertTrue(self.testcontroller)

    def test_index(self):
        doc = Document.objects.get(pk=1)
        res = self.testcontroller.index_one_doc(doc)
        self.assertTrue(res['ok'])
        self.assertEqual(res['_id'],'1')
    
        res = self.testcontroller._es.get(index=self.testcontroller._es_index,doc_type=self.testcontroller._doc_type,id=1)
        self.assertTrue(res['exists'])
    
        self.testcontroller.delete_one_doc(1)
        
        self.assertRaises(NotFoundError,self.testcontroller._
        self.assertFalse(res['exists'])

    def _get_deleted(self):
        
        self.testcontroller._es.get(index=self.testcontroller._es_index,doc_type=self.testcontroller._doc_type,id=1)
    
    def test_search(self):
        res = self.testcontroller.search_raw_result('test',10,0)
        self.assertFalse(res['timed_out'])

if __name__ == '__main__':
        unittest.main()
