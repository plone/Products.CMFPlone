## Script (Python) "login_initial"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Handle a user's initial login
##

if context.validate_email:
    state.set(status='login_change_password')
return state
