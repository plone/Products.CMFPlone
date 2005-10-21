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
from Products.CMFPlone import PloneMessageFactory as _

REQUEST=context.REQUEST
msg = _(u'No change has been done.')

if addname:
    context.portal_groups.addGroup(addname,(),())
    group=context.portal_groups.getGroupById(addname)
    msg = _(u'Group ${name} has been added.')
    msg.mapping[u'name'] = addname
else:
    group=context.portal_groups.getGroupById(groupname)
    msg = _(u'Changes saved.')

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
