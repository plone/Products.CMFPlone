## Script (Python) "change_password"
##title=Action to change password
##parameters=password, confirm, domains=None
if context.REQUEST.form.has_key('cancel'):
    context.REQUEST.set('portal_status_message', 'Password change was canceled.')
    return context.personalize_form()
								    

mt = context.portal_membership
failMessage=context.portal_registration.testPasswordValidity(password, confirm)
if failMessage:
  context.REQUEST.set('portal_status_message', failMessage)
  return context.password_form(context,
                               context.REQUEST,
                               error=failMessage)
			       
member = mt.getAuthenticatedMember()
mt.setPassword(password, domains)
mt.credentialsChanged(password)
context.REQUEST.set('portal_status_message', 'Password changed.')
return context.personalize_form(context,
                                context.REQUEST,
                                portal_status_message='Password changed.')
