## Script (Python) "collector_search.py"
##title=Build Collector Search

query = {}
query['sort_on'] = 'created'
query['Type'] = "Collector Issue"

reqget = context.REQUEST.get
subj_items = []

def supplement_query(field, index_name=None, reqget=reqget, query=query):
    if not index_name: index_name = field
    val = reqget(field, None)
    if val:
        query[index_name] = val

supplement_query("SearchableText")
supplement_query("Creator")
supplement_query("classifications", "classification")
supplement_query("topics", "topic")
supplement_query("supporters", "assigned_to")
supplement_query("resolution")
supplement_query("version_info")
supplement_query("importances", "importance")

sr = reqget("security_related", [])
if sr:
    if 'Yes' in sr and 'No' in sr:
        # Both means we don't care - don't include in query.
        pass
    elif 'Yes' in sr:
        query['security_related'] = [1]
    else:
        query['security_related'] = [0]

rs = []

for i in reqget("status", []):
    rs.append(i)
    # Include confidential alternatives to selected states.
    # XXX To account for changes, we should obtain all the possible states,
    #     and just do token processing according to their names.
    if i in ['Pending', 'Accepted']:
        rs.append("%s_confidential" % i)
    if rs:
        query['status'] = rs

got = context.get_internal_catalog()(REQUEST=query)
return got
