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
user = context.portal_membership.getAuthenticatedMember()
checkPermission=context.portal_membership.checkPermission
wf_wlist_map = context.portal_workflow.getWorklists()
catalog=context.portal_catalog
unique_catalog_vars = {}# dict with var:uniqueValuesFor
avail_objs = {} # absolute_url:obj - enables easier filtering

for wlist_map_sequence in wf_wlist_map.values():
    for wlist_map in wlist_map_sequence:
        permission=wlist_map['guard_permissions']
        catalog_vars=wlist_map['catalog_vars']
        # Filter out if we already know there is nothing in the catalog
        skip = 0
        for key,value in catalog_vars.items():
            if not unique_catalog_vars.has_key(key):
                unique_catalog_vars[key] = catalog.uniqueValuesFor(key)
            if not [val for val in value if val in unique_catalog_vars[key]]:
                # Nothing in the catalog, skip to next worklist
                skip = 1
                continue

        # Make sure we have types using this workflow/worklist
        if not skip and wlist_map.get('types',[]):
            for result in catalog.searchResults(catalog_vars, portal_type=wlist_map['types']):
                o = result.getObject()
                if o is not None and checkPermission(permission, o) \
                  and (not wlist_map['guard_roles'] \
                       or  wlist_map['guard_roles'] \
                       and [role for role in wlist_map['guard_roles'] if role in user.getRolesInContext(o)]) \
                  and not avail_objs.has_key(o.absolute_url()):
                    avail_objs[o.absolute_url()] = o

avail_objs = avail_objs.values()
avail_objs.sort(lambda x, y: cmp(x.modified(), y.modified()))
return avail_objs
