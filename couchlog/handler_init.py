import logging
from couchlog import config 


def init_handler():
    from couchlog.handlers import CouchHandler
    for handler in logging.root.handlers:
        if isinstance(handler, CouchHandler):
            # already set, do nothing
            return
    handler = CouchHandler()
    # the log_threshold is the ini value for what level the error handler should listen for
    # if it's less than the threshold set, the handler will never trigger.
    handler.level = config.COUCHLOG_THRESHOLD
    logging.root.addHandler(handler)


if config.COUCHLOG_ENABLED:
    # Initialize and register the handler
    init_handler()
