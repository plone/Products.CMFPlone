
pu=context.plone_utils
acquired_roles=pu.getInheritedLocalRoles(context)
local_roles=context.acl_users.getLocalRolesForDisplay(context)

# result contains dictionaries with the keys
# name, type, global_roles, acquired_roles, local_roles
result=[]

result1={}

# first process acquired roles
for name, roles, type, id in acquired_roles:
    result1[name]={
	'id'		: id,
	'name'		: name,
	'type'		: type,
	'global'	: [],
	'acquired'	: roles,
	'local'		: []
    }

# second process local roles
for name, roles, type, id in local_roles:
    if result1.has_key(name):
	result1[name]['local']=roles
    else:
	result1[name]={
	    'id'                : id,
	    'name'              : name,
	    'type'              : type,
	    'global'            : [],
	    'acquired'	        : [],
	    'local'		: roles 
	}

# XXX: process global roles

# now sort the list: first groups, then users, and then alphabetically

def sortfunc(a,b):
    # move Owner to top
    if 'Owner' in a['local']: return -1
    if 'Owner' in b['local']: return 1

    # compare type (groups up!)
    if a['type']==b['type']:
        # compare by name
        return cmp(a['name'],b['name'])
    else:
        if a['type']=='group': 
            return -1 
    return 1

result=result1.values()
result.sort(sortfunc)

return result



