## Script (Python) "deleteDiscussion"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=obj=None
##title=Delete discussion item
##
if obj is None:
    obj=context
		
parent = obj.inReplyTo()
talkback = context.portal_discussion.getDiscussionFor(parent)
return str(talkback.getReplies())
talkback.deleteReply( obj.getId() )

context.REQUEST['RESPONSE'].redirect( parent.absolute_url()
         + '?portal_status_message=Reply+deleted' )
