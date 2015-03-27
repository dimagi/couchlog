Couchlog
--------

[![Build Status](https://travis-ci.org/dimagi/couchlog.png?branch=master)](https://travis-ci.org/dimagi/couchlog)
[![Test coverage](https://coveralls.io/repos/dimagi/couchlog/badge.png?branch=master)](https://coveralls.io/r/dimagi/couchlog)
[![PyPi version](https://pypip.in/v/couchlog/badge.png)](https://pypi.python.org/pypi/couchlog)
[![PyPi downloads](https://pypip.in/d/couchlog/badge.png)](https://pypi.python.org/pypi/couchlog)

A django and couch-based logger for all your distributed error-tracking needs.

To configure (Django 1.3+) just add a line like this to your `LOGGING` setting (which is
based on [logging.config.dictConfig](http://docs.python.org/2/library/logging.config.html))

```
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
```

By default couchlog views require superuser permissions, but you can override it by setting COUCHLOG_AUTH_DECORATOR in settings.py to a different permission decorator.
