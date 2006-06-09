## Script (Python) "getPlonePersonalPortrait"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=member=None
##title=
##
context.plone_log("The getPlonePersonalPortrait script is deprecated and will be "
                  "removed in plone 3.5.")
return context.portal_membership.getPersonalPortrait(member)
