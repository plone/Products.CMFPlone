## Script (Python) "discussion_reply"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=title,text,Creator
##title=Reply to content

permCheck = context.portal_membership.checkPermission
from Products.PythonScripts.standard import url_quote_plus

Creator=context.portal_membership.getAuthenticatedMember().getUserName()

if permCheck('Reply to item',context):
    replyID = context.createReply( title = title
                             , text = text
                             , Creator = Creator )
else:
    REQUEST=context.REQUEST
    came_from=REQUEST['URL']+'?'+('&'.join([fp[0]+'='+fp[1] for fp in REQUEST.form.items()]))
    
    return REQUEST.RESPONSE.redirect('login_form?came_from='+str(url_quote_plus(came_from)))

target = '%s/%s' % (context.aq_parent.absolute_url(), context.aq_parent.getTypeInfo().getActionById('view'))

context.REQUEST.RESPONSE.redirect(target)

