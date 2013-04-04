function (doc) {
    try {
        if (doc.doc_type == "ExceptionRecord")
        {

            index("date", doc.date);
            if (doc.level) {
                index("level", doc.level);
            }
            if (doc.archived) {
                index("default", "archived");
            }
            var fields = ["message", "url", "type", "extra_info"];
            for (var i = 0; i < fields.length; i++) {
                var field = fields[i];
                if (doc[field]) {
                    index("default", doc[field]);
                }
            }
        }
    }
    catch (err) {
        // search may not be configured, do nothing
    }
}