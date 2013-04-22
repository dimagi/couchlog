from django.test import TestCase
from django.conf import settings
from couchlog.models import ExceptionRecord
import logging
from dimagi.utils.couch.database import get_safe_write_kwargs


class LogTestCase(TestCase):
    
    def setUp(self):
        db = ExceptionRecord.get_db()
        for row in db.view("couchlog/all_by_date").all():
            db.delete_doc(row['id'], **get_safe_write_kwargs())
    
    def testThreshold(self):
        # makes the shady assumption that the couchlog threshold is above debug
        self.assertEqual(0, len(ExceptionRecord.view("couchlog/all_by_date", include_docs=True).all()))
        logging.debug("Don't write me to couchlog!")
        self.assertEqual(0, len(ExceptionRecord.view("couchlog/all_by_date", include_docs=True).all()))
        # make sure we're not dependent on the root log level
        logging.root.setLevel(logging.DEBUG)
        logging.debug("Don't write me to couchlog either!")
        self.assertEqual(0, len(ExceptionRecord.view("couchlog/all_by_date", include_docs=True).all()))
        
        
        
    def testCreation(self):
        self.assertEqual(0, len(ExceptionRecord.view("couchlog/all_by_date", include_docs=True).all()))
        logging.error("Fail!")
        self.assertEqual(1, len(ExceptionRecord.view("couchlog/all_by_date", include_docs=True).all()))
        log = ExceptionRecord.view("couchlog/all_by_date", include_docs=True).one()
        self.assertEqual("Fail!", log.message)
        self.assertTrue("tests.py" in log.pathname)
        self.assertFalse(log.archived)
        
    def testFromException(self):
        self.assertEqual(0, len(ExceptionRecord.view("couchlog/all_by_date", include_docs=True).all()))
        class CouchLogTestException(Exception): pass 
        try:
            raise CouchLogTestException("Exceptional fail!")
        except Exception, e:
            logging.exception("some other message")
        
        self.assertEqual(1, len(ExceptionRecord.view("couchlog/all_by_date", include_docs=True).all()))
        log = ExceptionRecord.view("couchlog/all_by_date", include_docs=True).one()
        self.assertTrue("tests.py" in log.stack_trace)
        self.assertTrue("CouchLogTestException" in log.type)
        self.assertEqual("some other message", log.message)
        
        
    