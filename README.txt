A django and couch-based logger for all your distributed error-tracking needs.

To configure (Django 1.3+) just add a line like this to your LOGGING setting:

LOGGING = {
    'handlers': {
        'couchlog':{
            'level':'INFO',
            'class':'couchlog.handlers.CouchHandler',
        },
    },
    'loggers': {
        '': {
            'handlers':['couchlog'],
            'propagate': True,
            'level':'INFO',
        },
    }
}


