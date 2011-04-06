from django.conf import settings
import logging

LUCENE_ENABLED = getattr(settings, "LUCENE_ENABLED", False)
COUCHLOG_LUCENE_VIEW = getattr(settings, "COUCHLOG_LUCENE_VIEW", "couchlog/search")
COUCHLOG_LUCENE_DOC_TEMPLATE = getattr(settings, "COUCHLOG_LUCENE_DOC_TEMPLATE", "couchlog/lucene_docs.html")
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

# We don't bother shipping with these libraries, but if you want to import them from your own 
# servers just add these configuration params to localsettings.
COUCHLOG_JQUERY_LOC = getattr(settings, "COUCHLOG_JQUERY_LOC", 
                                   "https://ajax.googleapis.com/ajax/libs/jquery/1.4.3/jquery.min.js")
COUCHLOG_JQUERYUI_LOC = getattr(settings, "COUCHLOG_JQUERYUI_LOC", 
                                    "https://ajax.googleapis.com/ajax/libs/jqueryui/1.8.7/jquery-ui.min.js")
COUCHLOG_JQUERYUI_CSS_LOC = getattr(settings, "COUCHLOG_JQUERYUI_CSS_LOC", 
                                    "https://ajax.googleapis.com/ajax/libs/jqueryui/1.8.7/themes/smoothness/jquery-ui.css")
COUCHLOG_JQMODAL_LOC = getattr(settings, "COUCHLOG_JQMODAL_LOC", 
                                   "http://dev.iceburg.net/jquery/jqModal/jqModal.js")
COUCHLOG_JQMODAL_CSS_LOC = getattr(settings, "COUCHLOG_JQMODAL_CSS_LOC", 
                                   "http://dev.iceburg.net/jquery/jqModal/jqModal.css")
COUCHLOG_DATATABLES_LOC = getattr(settings, "COUCHLOG_DATATABLES_LOC", 
                                  "http://www.datatables.net/download/build/jquery.dataTables.min.js")
COUCHLOG_BLUEPRINT_HOME = getattr(settings, "COUCHLOG_BLUEPRINT_HOME", 
                                  "https://github.com/joshuaclayton/blueprint-css/raw/master/blueprint/")