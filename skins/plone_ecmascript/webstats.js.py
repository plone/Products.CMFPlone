## Script (Python) "webstats.js.py"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Output the script in the webstats_js site property 
##

from Products.CMFCore.utils import getToolByName
ptool=getToolByName(context, 'portal_properties')
site_props = ptool.site_properties

out = site_props.getProperty('webstats_js','')

return out
