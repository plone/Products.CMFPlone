## Script (Python) "isDefaultPageInFolder"
##title=Find out if the current context is the default page in its parent
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=

from Products.CMFCore.utils import getToolByName
ptool = getToolByName(context, 'plone_utils')

defaultPageId = ptool.getDefaultPage(context.aq_inner.aq_parent)
if defaultPageId == context.getId():
    return True
else:
    return False