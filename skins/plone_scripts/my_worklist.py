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
        permissions=wlist_map['guard_permissions']
        roles=wlist_map['guard_roles']
        catalog_vars=wlist_map['catalog_vars']
        types=wlist_map['types']
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
        if not skip and types:
            for result in catalog.searchResults(catalog_vars, portal_type=types):
                o = result.getObject()
                if o:
                    absurl = o.absolute_url()
                    if o is not None \
                      and not avail_objs.has_key(absurl) \
                      and (not permissions \
                           or  permissions \
                           and [p for p in permissions if checkPermission(p, o)]) \
                      and (not roles \
                           or  roles \
                           and [role for role in user.getRolesInContext(o) if role in roles]):
                        avail_objs[absurl] = o

avail_objs = avail_objs.values()
avail_objs.sort(lambda x, y: cmp(y.modified(), x.modified()))
return avail_objs
