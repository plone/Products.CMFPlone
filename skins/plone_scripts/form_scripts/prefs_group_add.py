## Script (Python) "prefs_group_add"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Add group
##
from Products.PythonScripts.standard import url_quote

REQUEST=context.REQUEST
name = REQUEST['addname']
context.portal_groups.addGroup(name,"",(),())
url='%s?%s=%s' % (context.prefs_group_details.absolute_url(),
	url_quote('groupname'),
	url_quote(name))
return REQUEST.RESPONSE.redirect(url)
