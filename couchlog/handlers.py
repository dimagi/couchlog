from logging import Handler
import sys

class CouchHandler(Handler):
    """Log in couch!"""   
    
    def __init__(self):
        # this is a required line
        Handler.__init__(self)

    def emit(self, record,  *args, **kwargs):
        from couchlog.models import ExceptionRecord 
        try:
            # create log here
            ExceptionRecord.from_log_record(record)
        except Exception:
            # TODO: maybe do something more here.  Logging shouldn't blow
            # up anything else, but at the same time we'd still like to 
            # know that something went wrong.
            # unfortunately we can't really log it, as that could land us in
            # an infinite loop.
            pass
