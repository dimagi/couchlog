from datetime import datetime
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.http import HttpResponse
from django.views.decorators.http import require_POST
import json
from django.conf import settings
from django.core.mail import send_mail, EmailMessage
from django.template.loader import render_to_string
from django.utils.text import truncate_words
from couchdbkit.client import View
from django.utils.html import escape
from django.core.urlresolvers import reverse
from django.contrib.sites.models import Site

from dimagi.utils.couch.database import get_db
from couchlog.models import ExceptionRecord
from dimagi.utils.couch.pagination import CouchPaginator, LucenePaginator
from couchlog import config 
import logging

def dashboard(request):
    """
    View all couch error data
    """
    show = request.GET.get("show", "inbox")
    # there's a post mechanism to do stuff here.  currently all it can do is 
    # bulk archive a search
    if request.method == "POST":
        op = request.POST.get("op", "")
        if op == "bulk_archive":
            query = request.POST.get("query", "")
            if query:
                def get_matching_records(query):
                    if config.LUCENE_ENABLED:
                        query = "%s AND NOT archived" % query
                        limit = get_db().search("couchlog/search", handler="_fti/_design", 
                                                q=query, limit=1).total_rows
                        matches = get_db().search("couchlog/search", handler="_fti/_design", 
                                                  q=query, limit=limit, include_docs=True)
                        return [ExceptionRecord.wrap(res["doc"]) for res in matches]
                        
                    else:
                        return ExceptionRecord.view("couchlog/inbox_by_msg", reduce=False, key=query).all() 
                records = get_matching_records(query)
                for record in records:
                    record.archived = True
                ExceptionRecord.bulk_save(records)    
                            
    return render_to_response('couchlog/dashboard.html',
                              {"show" : show, "count": True,
                               "lucene_enabled": config.LUCENE_ENABLED,
                               "support_email": config.SUPPORT_EMAIL },
                               context_instance=RequestContext(request))

def single(request, log_id, display="full"):
    log = ExceptionRecord.get(log_id)
    if request.method == "POST":
        action = request.POST.get("action", None)
        username = request.user.username if request.user and not request.user.is_anonymous() else "unknown"
        if action == "archive":
            log.archive(username)
        elif action == "move_to_inbox":
            log.reopen(username)
    
    if display == "ajax":
        template = "couchlog/ajax/single.html"
    elif display == "full":
        template = "couchlog/single.html"
    else:
        raise ValueError("Unknown display type: %s" % display)
    return render_to_response(template, 
                              {"log": log},
                              context_instance=RequestContext(request))


def _record_to_json(error):
    """Shared by the wrappers"""
    def truncate(message, length=100, append="..."):
        if length < len(append):
            raise Exception("Can't truncate to less than %s characters!" % len(append))
        return "%s%s" % (message[:length], append) if len(message) > length else message
     
    def format_type(type):
        return escape(type)
    
    return [error.get_id,
            error.archived, 
            error.date.strftime('%Y-%m-%d %H:%M:%S') if error.date else "", 
            format_type(error.type), 
            truncate(error.message), 
            error.url,
            "archive",
            "email"]
    

def lucene_search(request, search_key, show_all):
    
    def wrapper(row):
        id = row["id"]
        doc = ExceptionRecord.get(id)
        return _record_to_json(doc)
    
    if not show_all:
        search_key = "%s AND NOT archived" % search_key
    total_records = get_db().view("couchlog/count").one()["value"]
    paginator = LucenePaginator("couchlog/search", wrapper)
    return paginator.get_ajax_response(request, search_key, extras={"iTotalRecords": total_records})
                                    
    
def paging(request):
    
    # what to show
    query = request.POST if request.method == "POST" else request.GET
    
    search_key = query.get("sSearch", "")
    show_all = query.get("show", "inbox") == "all"
    if search_key:
        if config.LUCENE_ENABLED:
            return lucene_search(request, search_key, show_all)
        view_name = "couchlog/all_by_msg" if show_all else "couchlog/inbox_by_msg"
        search = True
    else:
        view_name = "couchlog/all_by_date" if show_all else "couchlog/inbox_by_date"
        search = False
    
    def wrapper_func(row):
        """
        Given a row of the view, get out an exception record
        """
        error = ExceptionRecord.wrap(row["value"])
        return _record_to_json(error)
        
    paginator = CouchPaginator(view_name, wrapper_func, search=search)
    
    # get our previous start/end keys if necessary
    # NOTE: we don't actually do anything with these yet, but we should for 
    # better pagination down the road.  using the "skip" parameter is not
    # super efficient.
    startkey = query.get("startkey", None)
    if startkey:
        startkey = json.loads(startkey)
    endkey = query.get("endkey", None)
    if endkey:
        endkey = json.loads(endkey)
    
    total_records = get_db().view("couchlog/count").one()["value"]
    
    return paginator.get_ajax_response(request, extras={"startkey": startkey,
                                                        "endkey": endkey,
                                                        "iTotalRecords": total_records})
                                    
        


@require_POST
def update(request):
    """
    Update a couch log.
    """
    id = request.POST["id"]
    action = request.POST["action"]
    if not id:
        raise Exception("no id!")
    log = ExceptionRecord.get(id)
    username = request.user.username if request.user and not request.user.is_anonymous() else "unknown"
    if action == "archive":
        log.archive(username)
        text = "archived! press to undo"
        next_action = "move_to_inbox"
    elif action == "move_to_inbox":
        log.reopen()
        text = "moved! press to undo"
        next_action = "archive"
    to_return = {"id": id, "text": text, "next_action": next_action,
                 "action": action, 
                 "style_class": "archived" if log.archived else "inbox"}
    return HttpResponse(json.dumps(to_return))
    
@require_POST
def email(request):
    """
    Update a couch log.
    """
    id = request.POST["id"]
    to = request.POST["to"].split(",")
    print "email to: %s" % to
    notes = request.POST["notes"]
    log = ExceptionRecord.get(id)
    if request.user and not request.user.is_anonymous():
        name = request.user.get_full_name()
        username = request.user.username
        reply_to = "%s <%s>" % (request.user.get_full_name(), request.user.email)
    else:
        name = ""
        username = "unknown"
        reply_to = settings.EMAIL_HOST_USER
    
    url = "http://%s%s" % (Site.objects.get_current().domain, reverse("couchlog_single", args=[id]))
    email_body = render_to_string("couchlog/email.txt",
                                  {"user_info": "%s (%s)" % (name, username),
                                   "notes": notes,
                                   "exception_url": url})
    
    try:
        email = EmailMessage("[COUCHLOG ERROR] %s" % truncate_words(log.message, 10), 
                             email_body, name,
                             to, 
                             headers = {'Reply-To': reply_to})
        email.send(fail_silently=False)
        return HttpResponse(json.dumps({"id": id,
                                        "success": True}))
    except Exception, e:
        logging.exception(e)
        return HttpResponse(json.dumps({"id": id,
                                        "success": False, 
                                        "message": str(e)}))
        
def lucene_docs(request):
    return render_to_response("couchlog/lucene_docs.html", RequestContext(request))
