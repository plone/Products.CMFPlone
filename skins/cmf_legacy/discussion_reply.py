## Script (Python) "discussion_reply"
##parameters=title,text
##title=Reply to content

Creator = context.portal_membership.getAuthenticatedMember().getUserName()
replyID = context.createReply( title = title
                             , text = text
                             , Creator = Creator
                             )

target = '%s/%s' % (context.absolute_url(), replyID)

context.REQUEST.RESPONSE.redirect(target)

