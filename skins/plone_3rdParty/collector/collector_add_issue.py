## Script (Python) "collector_add_issue.py"
##parameters=title, security_related, submitter_email, topic, importance, classification, description, version_info
##title=Submit a Request

from Products.PythonScripts.standard import url_quote_plus

REQGET = context.REQUEST.get

id, err = context.add_issue(title=title,
                            security_related=security_related,
                            submitter_name=REQGET('submitter_name'),
                            submitter_email=submitter_email,
                            description=description,
                            topic=topic,
                            classification=classification,
                            importance=importance,
                            version_info=version_info,
                            assignees=REQGET('assignees', []),
                            file=REQGET('file'),
                            fileid=REQGET('fileid', ''),
                            filetype=REQGET('filetype', 'file'))

dest = "%s/%s" % (context.absolute_url(), id)
if err:
    dest += '?portal_status_message=' + url_quote_plus(err)

context.REQUEST.RESPONSE.redirect(dest)

