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
if name:
  context.portal_groups.addGroup(name,"",(),())
  url='%s?%s=%s' % (context.prefs_group_details.absolute_url(),
	url_quote('groupname'),
	url_quote(name))
else:
  url='%s?%s=%s' % (context.prefs_groups_overview.absolute_url(),
	url_quote('portal_status_message'),
	url_quote('Please choose a name for the group.'))

return REQUEST.RESPONSE.redirect(url)
