from django.conf import settings
import logging

LUCENE_ENABLED = getattr(settings, "LUCENE_ENABLED", False)
COUCHLOG_LUCENE_VIEW = getattr(settings, "COUCHLOG_LUCENE_VIEW", "couchlog/search")
SUPPORT_EMAIL = getattr(settings, "SUPPORT_EMAIL", None)

COUCHLOG_ENABLED = getattr(settings, "COUCHLOG_ENABLED", True)
COUCHLOG_THRESHOLD = getattr(settings, "COUCHLOG_THRESHOLD", logging.ERROR)


_DEFAULT_TABLE_CONFIG = {"id_column":       0,
                         "archived_column": 1,
                         "date_column":     2,
                         "message_column":  4,
                         "actions_column":  6,
                         "email_column":    7,
                         "no_cols":         8}

_DEFAULT_DISPLAY_COLS = ["id", "archived?", "date", "", "message", "url", "actions", "report"]

COUCHLOG_TABLE_CONFIG = getattr(settings, "COUCHLOG_TABLE_CONFIG", _DEFAULT_TABLE_CONFIG)
COUCHLOG_DISPLAY_COLS = getattr(settings, "COUCHLOG_DISPLAY_COLS", _DEFAULT_DISPLAY_COLS)
COUCHLOG_RECORD_WRAPPER = getattr(settings, "COUCHLOG_RECORD_WRAPPER", None)
    