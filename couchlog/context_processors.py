from django.conf import settings

def static_workaround(request):
    return {
        # hack for django staticfiles + couchlog support
        # if you don't have django-staticfiles installed add this to your 
        # context processors:
        # "couchlog.context_processors.static_workaround",
        "STATIC_URL": "%s%s" % (settings.MEDIA_URL, "couchlog/")
    }
