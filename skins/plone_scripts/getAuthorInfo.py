## Script (Python) "getAuthor"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=memberid
##title=get author information
##
from Products.CMFCore.utils import getToolByName

mtool = getToolByName(context, 'portal_membership', None)

if mtool is None:
    return None

member = mtool.getMemberById(memberid)

if member is None:
    return None

# add additional attributes such as location, etc once required
# make sure sensitive information (i.e. email) is not accessible
memberinfo = { 'fullname':member.getProperty('fullname') }

return memberinfo
