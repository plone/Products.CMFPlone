## Script (Python) "getPlonePersonalPortrait"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=member=None
##title=
##
try:
  home=context.portal_membership.getHomeFolder(member)
  personal=getattr(home, '.personal', None) 
  if personal:
    portrait=getattr(personal, 'MyPortrait', None)
    if portrait:         
        return portrait
except:
  pass
