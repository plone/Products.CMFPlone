## Script (Python) "my_worklist"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=time=None
##title=
##

if context.portal_membership.isAnonymousUser():
    return []

wf_wlist_map = context.getWorklists() #getWorklists is currently a external method ;(
catalog=context.portal_catalog
avail_objs = []

for wlist_map_sequence in wf_wlist_map.values():
    for wlist_map in wlist_map_sequence:
        permission=wlist_map['guard_permissions']
        catalog_vars=wlist_map['catalog_vars']
        if context.portal_membership.checkPermission(permission, container):
            for result in catalog.searchResults(catalog_vars):
                if result.getURL() not in [o.absolute_url() for o in avail_objs]:
                    avail_objs.append(result.getObject())

return avail_objs

