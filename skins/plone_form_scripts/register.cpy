## Controller Python Script "register"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=password='password', confirm='confirm', came_from_prefs=None
##title=Register a User
##

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
        #XXX registerdNotify calls into various levels.  Lets catch all exceptions.
        #    Should not fail.  They cant CHANGE their password ;-)  We should notify them.
        state.set(portal_status_message='We were unable to send your password to your email address.')
        state.set(came_from='logged_in')
        return state
        
state.set(portal_status_message=REQUEST.get('portal_status_message', 'Registered.'))
state.set(came_from=REQUEST.get('came_from','logged_in'))

if came_from_prefs:
    state.set(status='prefs')

from Products.CMFPlone import transaction_note
transaction_note('%s registered' % username)

return state
