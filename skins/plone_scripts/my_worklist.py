## Script (Python) "my_worklist"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##

if context.portal_membership.isAnonymousUser():
    return []

checkPermission=context.portal_membership.checkPermission
wf_wlist_map = context.portal_workflow.getWorklists() #getWorklists is currently a external method ;(
catalog=context.portal_catalog
avail_objs = []

for wlist_map_sequence in wf_wlist_map.values():
    for wlist_map in wlist_map_sequence:
        permission=wlist_map['guard_permissions']
        catalog_vars=wlist_map['catalog_vars']

        for result in catalog.searchResults(catalog_vars):
            o = result.getObject()
            if o is not None and checkPermission(permission, o) \
            and o.absolute_url() not in [ a.absolute_url()
                                          for a in avail_objs ]:
                avail_objs.append(o)

avail_objs.sort(lambda x, y: cmp(x.modified(), y.modified()))
return avail_objs
