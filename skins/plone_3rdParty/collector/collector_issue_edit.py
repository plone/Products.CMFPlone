## Script (Python) "collector_issue_edit.py"
##title=Submit a Request

from Products.PythonScripts.standard import url_quote_plus

REQGET = context.REQUEST.get

was_security_related = context.security_related

changed = context.edit(title=REQGET('title'),
                       submitter_id=REQGET('submitter_id', None),
                       submitter_name=REQGET('submitter_name', None),
                       submitter_email=REQGET('submitter_email', None),
                       security_related=REQGET('security_related', 0),
                       description=REQGET('description'),
                       topic=REQGET('topic'),
                       classification=REQGET('classification'),
                       importance=REQGET('importance'),
                       version_info=REQGET('version_info'),
                       comment=REQGET('comment'),
                       text=REQGET('text'))

if context.security_related != was_security_related:
    # We're toggling security_related - we have to do the corresponding
    # restrict/unrestrict if available in the current state:
    if context.security_related:
        seeking_pretty = 'Restrict'
    else:
        seeking_pretty = 'Unrestrict'
    for action, pretty in context.valid_actions_pairs():
        if pretty == seeking_pretty:
            context.do_action(action, ' Triggered by security_related toggle.')
            changed = changed + ", " + pretty.lower() + 'ed'
            break

whence = context.absolute_url()

if changed:
    msg = url_quote_plus("Changed: " + changed)
    context.REQUEST.RESPONSE.redirect("%s?portal_status_message=%s"
                                      % (whence, msg))

else:
    context.REQUEST.RESPONSE.redirect(whence)

