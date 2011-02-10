from django.conf import settings
import logging

LUCENE_ENABLED = getattr(settings, "LUCENE_ENABLED", False)
SUPPORT_EMAIL = getattr(settings, "SUPPORT_EMAIL", None)

COUCHLOG_ENABLED = getattr(settings, "COUCHLOG_ENABLED", True)
COUCHLOG_THRESHOLD = getattr(settings, "COUCHLOG_THRESHOLD", logging.ERROR)
