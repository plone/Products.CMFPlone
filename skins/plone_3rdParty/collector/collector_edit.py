## Script (Python) "collector_edit.py"
##parameters=title, description, email, abbrev, managers, supporters, dispatching, participation, state_email, topics, classifications, importances, version_info_spiel
##title=Configure Collector
 
from Products.PythonScripts.standard import url_quote_plus

changes = context.edit(title=title,
                       description=description,
                       abbrev=abbrev,
                       email=email,
                       managers=managers,
                       supporters=supporters,
                       dispatching=dispatching,
                       participation=participation,
                       state_email=state_email,
                       topics=topics,
                       classifications=classifications,
                       importances=importances,
                       version_info_spiel=version_info_spiel)

if not changes:
    changes = "No changes"
else:
    changes = "Changed: " + changes

recatalog = context.REQUEST.get('recatalog', None)
if recatalog:
    if recatalog == 1:
        context.reinstate_catalog(internal_only=1)
        changes += ", reinstated catalog, reindexed internally"
    else:
        context.reinstate_catalog(internal_only=0)
        changes += ", reinstated catalog, reindexed internally and site wide"

msg = '?portal_status_message=%s.' % url_quote_plus(changes)
 
context.REQUEST.RESPONSE.redirect("%s/%s%s"
                                  % (context.absolute_url(),
                                     "collector_edit_form",
                                     msg))

