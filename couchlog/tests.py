from django.test import TestCase
from django.conf import settings
from couchlog.models import ExceptionRecord
import logging

class LogTestCase(TestCase):
    
    def setUp(self):
        for item in ExceptionRecord.view("couchlog/all_by_date").all():
            item.delete()
    
    def testThreshold(self):
        # makes the shady assumption that the couchlog threshold is above debug
        self.assertEqual(0, len(ExceptionRecord.view("couchlog/all_by_date").all()))
        logging.debug("Don't write me to couchlog!")
        self.assertEqual(0, len(ExceptionRecord.view("couchlog/all_by_date").all()))
        # make sure we're not dependent on the root log level
        logging.root.setLevel(logging.DEBUG)
        logging.debug("Don't write me to couchlog either!")
        self.assertEqual(0, len(ExceptionRecord.view("couchlog/all_by_date").all()))
        
        
        
    def testCreation(self):
        self.assertEqual(0, len(ExceptionRecord.view("couchlog/all_by_date").all()))
        logging.error("Fail!")
        self.assertEqual(1, len(ExceptionRecord.view("couchlog/all_by_date").all()))
        log = ExceptionRecord.view("couchlog/all_by_date").one()
        self.assertEqual("Fail!", log.message)
        self.assertTrue("tests.py" in log.pathname)
        self.assertFalse(log.archived)
        
    def testFromException(self):
        self.assertEqual(0, len(ExceptionRecord.view("couchlog/all_by_date").all()))
        class CouchLogTestException(Exception): pass 
        try:
            raise CouchLogTestException("Exceptional fail!")
        except Exception, e:
            logging.exception(e)
        
        self.assertEqual(1, len(ExceptionRecord.view("couchlog/all_by_date").all()))
        log = ExceptionRecord.view("couchlog/all_by_date").one()
        self.assertTrue("tests.py" in log.stack_trace)
        self.assertTrue("CouchLogTestException" in log.type)
        self.assertEqual("Exceptional fail!", log.message)
        
        
    