## Script (Python) "getObjPositionInParent"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
from Products.CMFCore.utils import getToolByName
IDiscussable = 'Products.CMFCore.interfaces.IDiscussable'

interface = getToolByName(container, 'portal_interface')
parent = context.aq_inner.aq_parent

# Stupid, stupid DiscussionItemContainer...
if interface.objectImplements(parent, IDiscussable):
    return 0

getpos = getattr(parent.aq_inner.aq_explicit, 'getObjectPosition', None)
if getpos is not None:
    return getpos(context.getId())
else:
    return 0
