## Controller Python Script "register"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=password='password', confirm='confirm', came_from_prefs=None
##title=Register a User
##
state = context.portal_form_controller.getState(script, is_validator=0)

REQUEST=context.REQUEST

portal_registration=context.portal_registration
site_properties=context.portal_properties.site_properties

username = REQUEST['username']

password=REQUEST.get('password') or portal_registration.generatePassword()
portal_registration.addMember(username, password, properties=REQUEST)

if site_properties.validate_email or REQUEST.get('mail_me', 0):
    try:
        portal_registration.registeredNotify(username)
    except:
        state.setError('email', 'We were unable to send your password to this address.', new_status='failure')
        context.plone_utils.logException()
        exception = context.plone_utils.exceptionString()
        state.set(portal_status_message=exception)
        state.set(came_from=context.REQUEST.get('came_from','logged_in'))
        return state

state.set(portal_status_message=context.REQUEST.get('portal_status_message', 'Registered.'))
state.set(came_from=context.REQUEST.get('came_from','logged_in'))
if came_from_prefs:
    state.set(status='prefs')

return state
