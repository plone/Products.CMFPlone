## Script (Python) "getPlonePersonalPortrait"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=member=None
##title=
##
return context.portal_membership.getPersonalPortrait(member)
