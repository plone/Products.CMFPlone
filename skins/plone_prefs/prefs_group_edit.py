## Script (Python) "prefs_group_edit"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=addname=None, groupname=None
##title=Edit user
##
from Products.PythonScripts.standard import url_quote

REQUEST=context.REQUEST
msg = 'No changes done.'

if addname:
    context.portal_groups.addGroup(addname,(),())
    group=context.portal_groups.getGroupById(addname)
    msg = context.translate("Group ${name} has been added.",
                            {'name': addname})
else:
    group=context.portal_groups.getGroupById(groupname)
    msg = 'Changes saved.'

processed={}
for id, property in context.portal_groupdata.propertyItems():
    processed[id]=REQUEST.get(id, None)

if group:
    # for what reason ever, the very first group created does not exist
    group.setGroupProperties(processed)

url='%s?%s=%s' % (context.prefs_groups_overview.absolute_url(),
    url_quote('portal_status_message'),
    url_quote(msg))

return REQUEST.RESPONSE.redirect(url)
