## Script (Python) "deleteDiscussion"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=obj=None
##title=Delete discussion item

from Products.CMFPlone import PloneMessageFactory as _

if obj is None:
    obj = context

parent = obj.inReplyTo()
if parent is not None:
    from Products.CMFCore.utils import getToolByName
    dtool = getToolByName(context, 'portal_discussion')
    talkback = dtool.getDiscussionFor(parent)
else:
    talkback = parent = obj.aq_parent

# remove the discussion item
talkback.deleteReply(obj.getId())

# redirect to the object that is being discussed
redirect_target = context.plone_utils.getDiscussionThread(talkback)[0]
context.plone_utils.addPortalMessage(_(u'Reply deleted.'))

context.REQUEST['RESPONSE'].redirect(redirect_target.absolute_url() + '/view')
