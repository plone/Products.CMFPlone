## Script (Python) "removePlonePersonalPortrait"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=member=None
##title=
##
REQUEST=context.REQUEST
msg=''

home=context.portal_membership.getHomeFolder(member)
personal=getattr(home, '.personal', None) 
if personal and hasattr(personal, 'MyPortrait'):
    personal.manage_delObjects('MyPortrait')
    msg='portal_status_message=Personal+Portrait+has+been+deleted.'

url=context.absolute_url()+'/personalize_form'
return REQUEST.redirect( '%s?%s' % ( url, msg ) )
