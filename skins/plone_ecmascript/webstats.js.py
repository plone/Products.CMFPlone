## Script (Python) "webstats.js.py"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=REQUEST=None, RESPONSE=None
##title=Output the script in the webstats_js site property 
##

from Products.CMFCore.utils import getToolByInterfaceName
ptool=getToolByInterfaceName('Products.CMFCore.interfaces.IPropertiesTool')
site_props = ptool.site_properties

out = site_props.getProperty('webstats_js','')

return out
