import logging
from couchlog import config 

if config.COUCHLOG_ENABLED:
    # Initialize and register the handler
    from couchlog.handlers import CouchHandler
    handler = CouchHandler()
    # the log_threshold is the ini value for what level the error handler should listen for
    # if it's less than the threshold set, the handler will never trigger. 
    handler.level = config.COUCHLOG_THRESHOLD
    logging.root.addHandler(handler)