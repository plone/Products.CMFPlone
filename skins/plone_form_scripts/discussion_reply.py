## Script (Python) "discussion_reply"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=title,text,username=None,password=None
##title=Reply to content

from Products.PythonScripts.standard import url_quote_plus
req = context.REQUEST

if username or password:
    # The user username/password inputs on on the comment form were used,
    # which might happen when anonymous commenting is enabled. If they typed
    # something in to either of the inputs, we send them to 'logged_in'.
    # 'logged_in' will redirect them back to this script if authentication
    # succeeds with a query string which will post the message appropriately
    # and show them the result.  if 'logged_in' fails, the user will be
    # presented with the stock login failure page.  This all depends
    # heavily on cookiecrumbler, but I believe that is a Plone requirement.
    came_from = '%s?title=%s&amp;text=%s' % (req['URL'], title, text)
    came_from = url_quote_plus(came_from)
    portal_url = context.portal_url()

    return req.RESPONSE.redirect(
        '%s/logged_in?__ac_name=%s'
        '&amp;__ac_password=%s'
        '&amp;came_from=%s' % (portal_url,
                               url_quote_plus(username),
                               url_quote_plus(password),
                               came_from,
                               )
        )

# if (the user is already logged in) or (if anonymous commenting is enabled and
# they posted without typing a username or password into the form), we do
# the following

creator = context.portal_membership.getAuthenticatedMember().getUserName()
context.createReply(title=title, text=text, Creator=creator)

p = context.aq_parent
target = '%s/%s' % (p.absolute_url(),p.getTypeInfo().getActionById('view'))
return req.RESPONSE.redirect(target)
