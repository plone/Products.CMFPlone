## Script (Python) "prefs_valid_search_restriction.py"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=searchstring, restrict
##title=Valid Search Resriction
##
#MembershipTool.searchForMembers
groups_tool = context.portal_groups
members_tool = context.portal_membership
retlist = []

if not searchstring:
	if restrict != "groups":
		retlist = retlist + members_tool.listMembers()
	if restrict != "users":
		retlist = retlist + groups_tool.listGroups()
else:
	if restrict != "groups":
		retlist = retlist + members_tool.searchForMembers(REQUEST=None, name=searchstring)
	if restrict != "users":
		retlist = retlist + groups_tool.searchForGroups(REQUEST=None, name=searchstring)

# reorder retlist?
return retlist