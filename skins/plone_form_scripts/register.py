## Script (Python) "register"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=password='password', confirm='confirm'
##title=Register a User
##
REQUEST=context.REQUEST
errors = {}

portal_registration=context.portal_registration
site_properties=context.portal_properties.site_properties

username = REQUEST['username']

password=REQUEST.get('password') or portal_registration.generatePassword()
portal_registration.addMember(username, password, properties=REQUEST)

if site_properties.validate_email or REQUEST.get('mail_me', 0):
    try:
        portal_registration.registeredNotify(username)
    except:
        context.plone_utils.logException()
        exception = context.plone_utils.exceptionString()
        errors['email'] = 'We were unable to send your password to this address.'
        return ('failure', context, {'portal_status_message':exception,
                                     'errors':errors,
                                     'came_from':context.REQUEST.get('came_from','logged_in')})

return ('success', context, {'portal_status_message':context.REQUEST.get('portal_status_message', 'Registered.'),\
                             'came_from':context.REQUEST.get('came_from','logged_in')})
