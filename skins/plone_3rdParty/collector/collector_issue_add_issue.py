## Script (Python) "collector_issue_add_issue.py"
##title=Submit a Request

typeinfo = context.portal_types.getTypeInfo('Collector')
addissue = typeinfo.getActionById('addissue')

context.REQUEST.RESPONSE.redirect("%s/%s"
                                  % (context.aq_parent.absolute_url(),
                                     addissue))

