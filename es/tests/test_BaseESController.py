import unittest
import sys
sys.path.append('/home/ec2-user/bblio/es/')

from BaseESController import BaseESController, ESControllerError

class TestBaseESController(unittest.TestCase):
    def test_object(self):
        self.assertRaises(ESControllerError,BaseESController)
        #assertTrue(self.testcontroller)

if __name__ == '__main__':
        unittest.main()
