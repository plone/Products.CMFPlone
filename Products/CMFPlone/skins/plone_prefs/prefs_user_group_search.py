## Script (Python) "prefs_valid_search_restriction.py"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=searchstring, restrict, return_form=None, ignore=[]
##title=Valid Search Resriction
##
#MembershipTool.searchForMembers
groups_tool = context.portal_groups
members_tool = context.portal_membership
retlist = []

if restrict != "groups":
    retlist = retlist + members_tool.searchForMembers(REQUEST=None, name=searchstring)
if restrict != "users":
    retlist = retlist + groups_tool.searchForGroups(REQUEST=None, title_or_name=searchstring)

if ignore:
  retlist = [r for r in retlist if r not in ignore]

# reorder retlist?
if return_form:
    context.REQUEST.RESPONSE.redirect( context.absolute_url() + '/' + return_form )
return retlist
