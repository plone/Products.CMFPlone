## Script (Python) "prefs_group_edit"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=groupname
##title=Edit user
##
from Products.PythonScripts.standard import url_quote

REQUEST=context.REQUEST
group=context.portal_groups.getGroupById(groupname)

processed={}
for id, property in context.portal_groupdata.propertyItems():
    processed[id]=REQUEST.get(id, None)
    
group.setGroupProperties(processed)

#REFERER=REQUEST.HTTP_REFERER
#if REFERER.find('portal_status_message')!=-1:
#    REFERER=REFERER[:REFERER.find('portal_status_message')]
#url='%s&%s' % (REFERER, 'portal_status_message=Changes+made.')
#return REQUEST.RESPONSE.redirect(url)

url='%s?%s=%s' % (context.prefs_groups_overview.absolute_url(),
	url_quote('portal_status_message'),
	url_quote('Changes made.'))
return REQUEST.RESPONSE.redirect(url)
