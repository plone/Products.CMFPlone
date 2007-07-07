## Script (Python) "discussion_reply"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=subject,body_text,text_format='plain',username=None,password=None
##title=Reply to content

from Products.PythonScripts.standard import url_quote_plus
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import PloneMessageFactory as _
mtool = getToolByName(context, 'portal_membership')
dtool = getToolByName(context, 'portal_discussion')
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
    came_from = '%s?subject=%s&amp;body_text=%s' % (req['URL'], subject, body_text)
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

creator = mtool.getAuthenticatedMember().getId()
tb = dtool.getDiscussionFor(context)
id = tb.createReply(title=subject, text=body_text, Creator=creator)
reply = tb.getReply(id)

# TODO THIS NEEDS TO GO AWAY!
if hasattr(dtool.aq_explicit, 'cookReply'):
    dtool.cookReply(reply, text_format='plain')

parent = tb.aq_parent

# return to the discussable object.
redirect_target = context.plone_utils.getDiscussionThread(tb)[0]
view = redirect_target.getTypeInfo().getActionInfo('object/view',
                                                   redirect_target)['url']
anchor = reply.getId()

from Products.CMFPlone.utils import transaction_note
transaction_note('Added comment to %s at %s' % (parent.title_or_id(),
                                                reply.absolute_url()))

context.plone_utils.addPortalMessage(_(u'Comment added.'))
target = '%s#%s' % (view, anchor)
return req.RESPONSE.redirect(target)
