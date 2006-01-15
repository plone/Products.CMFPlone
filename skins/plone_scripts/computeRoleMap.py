
pu=context.plone_utils
acquired_roles=pu.getInheritedLocalRoles(context)
local_roles=context.acl_users.getLocalRolesForDisplay(context)

# result contains dictionaries with the keys
# name, type, global_roles, acquired_roles, local_roles
result=[]

result1={}

# first process acquired roles
for name, roles, type, id in acquired_roles:
    result1[id]={
	'id'		: id,
	'name'		: name,
	'type'		: type,
	'global'	: [],
	'acquired'	: roles,
	'local'		: []
    }

# second process local roles
for name, roles, type, id in local_roles:
    if result1.has_key(id):
	result1[id]['local']=roles
    else:
	result1[id]={
	    'id'                : id,
	    'name'              : name,
	    'type'              : type,
	    'global'            : [],
	    'acquired'	        : [],
	    'local'		: roles 
	}

# TODO: process global roles

# now sort the list: first Owner role, then groups, then users, and then alphabetically

result=result1.values()
dec_users = [('Owner' not in a['local'], a['type'], a['name'], a) for a in result]
dec_users.sort()
result = [a[-1] for a in dec_users]
return result



