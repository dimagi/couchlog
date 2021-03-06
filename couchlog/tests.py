import logging

from django.test import TestCase
from couchlog.handler_init import init_handler
from dimagi.utils.couch.database import safe_delete

from couchlog.models import ExceptionRecord
from couchlog.handlers import CouchHandler



class LogTestCase(TestCase):
    
    def setUp(self):
        # We want to support Python 2.6 a bit longer so we cannot use dictConfig here...
        # but it is so handy that we put it in settings.py instead of wrestle with crappy
        # imperative config
        self.logger = logging.getLogger('couchlog.tests')
        self.original_log_level = logging.root.getEffectiveLevel()
        for handler in list(self.logger.handlers):
            if isinstance(handler, CouchHandler):
                self.logger.removeHandler(handler)
        logging.root.setLevel(logging.ERROR)
        init_handler()

        self.db = ExceptionRecord.get_db()
        for row in self.db.view("couchlog/all_by_date").all():
            safe_delete(self.db, row['id'])

    def tearDown(self):
        logging.root.setLevel(self.original_log_level)

    def testThreshold(self):
        # makes the shady assumption that the couchlog threshold is above debug
        self.assertEqual(0, len(ExceptionRecord.view("couchlog/all_by_date", include_docs=True).all()))
        self.logger.debug("Don't write me to couchlog!")
        self.assertEqual(0, len(ExceptionRecord.view("couchlog/all_by_date", include_docs=True).all()))
        # make sure we're not dependent on the root log level
        self.logger.setLevel(logging.DEBUG)
        self.logger.debug("Don't write me to couchlog either!")
        self.assertEqual(0, len(ExceptionRecord.view("couchlog/all_by_date", include_docs=True).all()))


    def testCreation(self):
        self.assertEqual(0, len(ExceptionRecord.view("couchlog/all_by_date", include_docs=True).all()))
        self.logger.error("Fail!")
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
            self.logger.exception("some other message")

        docs = ExceptionRecord.view("couchlog/all_by_date", include_docs=True).all()
        self.assertEqual(1, len(ExceptionRecord.view("couchlog/all_by_date", include_docs=True).all()))
        log = ExceptionRecord.view("couchlog/all_by_date", include_docs=True).one()
        self.assertTrue("tests.py" in log.stack_trace)
        self.assertTrue("CouchLogTestException" in log.type)
        self.assertEqual("some other message", log.message)
