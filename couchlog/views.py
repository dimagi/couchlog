from dimagi.utils.web import get_url_base
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.http import HttpResponse, HttpResponseRedirect
from django.views.decorators.http import require_POST
import json
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils.html import escape
from django.core.urlresolvers import reverse

from couchlog.models import ExceptionRecord
from dimagi.utils.couch.pagination import CouchPaginator, LucenePaginator
from couchlog import config 
import logging
from django.contrib import messages
from django.contrib.auth.decorators import permission_required
from dimagi.utils.modules import to_function

def fail(request):
    # if you want to play with it, wire this to a url
    raise Exception("Couchlog simulated failure!")


import django
if django.VERSION < (1, 6):
    from django.utils.text import truncate_words
    class Truncator(object):
        def __init__(self, text):
            self.text = text

        def words(self, num):
            return truncate_words(self.text, num)

else:
    from django.utils.text import Truncator

@permission_required("is_superuser")
def dashboard(request):
    """
    View all couch error data
    """
    show = request.GET.get("show", "inbox")
    # there's a post mechanism to do stuff here.  currently all it can do is 
    # bulk archive a search
    if request.method == "POST":
        op = request.POST.get("op", "")
        query = request.POST.get("query", "")
        if query:
            def get_matching_records(query, include_archived):
                if config.LUCENE_ENABLED:
                    if not include_archived:
                        query = "%s AND NOT archived" % query
                    limit = ExceptionRecord.get_db().search(config.COUCHLOG_LUCENE_VIEW, handler="_fti/_design",
                                            q=query, limit=1).total_rows
                    matches = ExceptionRecord.get_db().search(config.COUCHLOG_LUCENE_VIEW, handler="_fti/_design",
                                              q=query, limit=limit, include_docs=True)
                    return [ExceptionRecord.wrap(res["doc"]) for res in matches]
                    
                else:
                    if include_archived:
                        return ExceptionRecord.view("couchlog/all_by_msg", reduce=False, key=query, include_docs=True).all() 
                    else:
                        return ExceptionRecord.view("couchlog/inbox_by_msg", reduce=False, key=query, include_docs=True).all() 
            if op == "bulk_archive":
                records = get_matching_records(query, False)
                for record in records:
                    record.archived = True
                ExceptionRecord.bulk_save(records)    
                messages.success(request, "%s records successfully archived." % len(records))
            elif op == "bulk_delete":
                records = get_matching_records(query, show != "inbox")
                rec_json_list = [record.to_json() for record in records]
                ExceptionRecord.get_db().bulk_delete(rec_json_list)
                messages.success(request, "%s records successfully deleted." % len(records))
    
    return render_to_response('couchlog/dashboard.html',
                              {"show" : show, "count": True,
                               "lucene_enabled": config.LUCENE_ENABLED,
                               "support_email": config.SUPPORT_EMAIL,
                               "config": config.COUCHLOG_TABLE_CONFIG,
                               "display_cols": config.COUCHLOG_DISPLAY_COLS,
                               "single_url_base": config.COUCHLOG_SINGLE_URL_BASE,
                               "couchlog_config": config},
                               context_instance=RequestContext(request))

@permission_required("is_superuser")
def single(request, log_id, display="full"):
    log = ExceptionRecord.get(log_id)
    if request.method == "POST":
        action = request.POST.get("action", None)
        username = request.user.username if request.user and not request.user.is_anonymous() else "unknown"
        if action == "delete":
            log.delete()
            messages.success(request, "Log was deleted!")
            return HttpResponseRedirect(reverse("couchlog_home"))
        elif action == "archive":
            log.archive(username)
            messages.success(request, "Log was archived!")
        elif action == "move_to_inbox":
            log.reopen(username)
            messages.success(request, "Log was moved!")
    
    if display == "ajax":
        template = "couchlog/ajax/single.html"
    elif display == "full":
        template = "couchlog/single.html"
    else:
        raise ValueError("Unknown display type: %s" % display)
    return render_to_response(template, 
                              {"log": log,
                               "couchlog_config": config},
                              context_instance=RequestContext(request))


def _record_to_json(error):
    """Shared by the wrappers"""
    if config.COUCHLOG_RECORD_WRAPPER:
        return to_function(config.COUCHLOG_RECORD_WRAPPER, failhard=True)(error)

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
            error.user,
            error.url,
            "archive",
            "email"]

def _couchlog_count():
    count_results = ExceptionRecord.get_db().view("couchlog/count").one()
    return count_results["value"] if count_results else 0

@permission_required("is_superuser")
def lucene_search(request, search_key, show_all):
    
    def wrapper(row):
        id = row["id"]
        doc = ExceptionRecord.get(id)
        return _record_to_json(doc)
    
    if not show_all:
        search_key = "%s AND NOT archived" % search_key
    
    total_records = _couchlog_count()
    paginator = LucenePaginator(config.COUCHLOG_LUCENE_VIEW, wrapper, 
                                database=ExceptionRecord.get_db())
    return paginator.get_ajax_response(request, search_key, extras={"iTotalRecords": total_records})
                                    
@permission_required("is_superuser")
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
        error = ExceptionRecord.wrap(row["doc"])
        return _record_to_json(error)
        
    paginator = CouchPaginator(view_name, wrapper_func, search=search, 
                               view_args={"include_docs": True},
                               database=ExceptionRecord.get_db())
    
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
    
    
    total_records = _couchlog_count()
    
    return paginator.get_ajax_response(request, extras={"startkey": startkey,
                                                        "endkey": endkey,
                                                        "iTotalRecords": total_records})
                                    
        


@require_POST
@permission_required("is_superuser")
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
        log.reopen(username)
        text = "moved! press to undo"
        next_action = "archive"
    elif action == "delete":
        log.delete()
        text = "deleted!"
        next_action = ""
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
    notes = request.POST["notes"]
    log = ExceptionRecord.get(id)
    if request.user and not request.user.is_anonymous():
        name = request.user.get_full_name()
        username = request.user.username
        reply_to = "%s <%s>" % (request.user.get_full_name(), request.user.email)
    else:
        name = ""
        username = "unknown"
        reply_to = config.SUPPORT_EMAIL

    url = "{}{}".format(get_url_base(), reverse("couchlog_single", args=[id]))
    email_body = render_to_string("couchlog/email.txt",
                                  {"user_info": "%s (%s)" % (name, username),
                                   "notes": notes,
                                   "exception_url": url})

    try:
        email = EmailMessage("[COUCHLOG ERROR] %s" % Truncator(log.message).words(10),
                             email_body, "%s <%s>" % (name, config.SUPPORT_EMAIL),
                             to, 
                             headers = {'Reply-To': reply_to})
        email.send(fail_silently=False)
        return HttpResponse(json.dumps({"id": id,
                                        "success": True}))
    except Exception, e:
        logging.exception("problem sending couchlog mail")
        return HttpResponse(json.dumps({"id": id,
                                        "success": False, 
                                        "message": str(e)}))

def lucene_docs(request):
    return render_to_response(config.COUCHLOG_LUCENE_DOC_TEMPLATE, 
                              {"couchlog_config": config},
                              context_instance=RequestContext(request))
