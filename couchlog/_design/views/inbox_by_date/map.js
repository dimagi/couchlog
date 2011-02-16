function(doc) { 
    if (doc.doc_type == "ExceptionRecord" && !doc.archived)
    {
        emit([new Date(doc.date)], null);
    }
}