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
if parent is not None:
    talkback = context.portal_discussion.getDiscussionFor(parent)
else:
    talkback = parent = obj.aq_parent

talkback.deleteReply( obj.getId() )

view = parent.getTypeInfo().getActionById('view')
context.REQUEST['RESPONSE'].redirect( parent.absolute_url()
         + '/%s?portal_status_message=Reply+deleted' % view )
