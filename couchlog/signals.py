from django.core.signals import got_request_exception
from django.conf import settings
from django.dispatch.dispatcher import Signal
#from dimagi.utils.logging.signals import exception_logged

couchlog_created = Signal(providing_args=["record"])

def log_request_exception(sender, request, **kwargs):
    from couchlog.models import ExceptionRecord
    record = ExceptionRecord.from_request_exception(request)
    record.save()
    
def log_standard_exception(sender, exc_info, **kwargs):
    from couchlog.models import ExceptionRecord
    record = ExceptionRecord.from_exc_info(exc_info)
    record.save()

#exception_logged.connect(log_standard_exception) TODO
got_request_exception.connect(log_request_exception)