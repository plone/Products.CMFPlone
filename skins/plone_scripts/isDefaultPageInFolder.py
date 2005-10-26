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

return ptool.isDefaultPage(context)
