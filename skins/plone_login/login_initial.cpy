## Controller Python Script "login_initial"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=
##title=Handle a user's initial login
##

# do anything that must be done during a user's initial login here

# afterwards, change the password if necessary
if state.getKwargs().get('must_change_password',0):
    state.set(status='login_change_password')
return state
