## Script (Python) "listMetaTags"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=(Deprecated, method in PloneTool.py now) List Dublin Core for '<meta>' tags
##
from Products.CMFCore.utils import getToolByName
plone_utils = getToolByName(context, 'plone_utils', None)

if plone_utils:
    return plone_utils.listMetaTags(context).items()
