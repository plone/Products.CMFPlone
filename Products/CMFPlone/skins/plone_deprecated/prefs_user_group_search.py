## Script (Python) "prefs_user_group_search.py"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=searchstring, restrict, return_form=None, ignore=[]
##title=Valid Search Resriction

#MembershipTool.searchForMembers

groups_tool = context.portal_groups
members_tool = context.portal_membership
groupsList = []
usersList = []

if restrict != "users":
    groupsList = groups_tool.searchForGroups(REQUEST=None,
                                             title_or_name=searchstring)
    groupsList.sort(key=lambda x: x.getGroupTitleOrName().lower())

if restrict != "groups":
    usersList = members_tool.searchForMembers(REQUEST=None, name=searchstring)
    usersList.sort(key=lambda x: x is not None
                                 and x.getProperty('fullname').lower()
                                 if x.getProperty('fullname')
                                 else x.getId().lower())

retlist = groupsList + usersList

if ignore:
    retlist = [r for r in retlist if r not in ignore]

# reorder retlist?
if return_form:
    context.REQUEST.RESPONSE.redirect(context.absolute_url()
                                      + '/'
                                      + return_form)
return retlist
