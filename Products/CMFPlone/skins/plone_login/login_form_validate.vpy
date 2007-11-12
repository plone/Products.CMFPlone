## Script (Python) "validate_login_form"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=
##title=Validate login
##

from Products.CMFPlone import PloneMessageFactory as _

request = context.REQUEST
js_enabled = request.get('js_enabled',0) # is javascript enabled?
js_enabled = js_enabled=='1' or js_enabled==1
cookies_enabled = request.get('cookies_enabled',0) # are cookies enabled?
cookies_enabled = cookies_enabled=='1' or cookies_enabled==1

if js_enabled and not cookies_enabled:
    context.plone_utils.addPortalMessage(_(u'You must enable cookies before you can log in.'), 'error')
    state.set(status='enable_cookies')
    return state

mt=context.portal_membership
if mt.isAnonymousUser():
    if js_enabled: # javascript is enabled - we can diagnose the failure
        auth = getattr(context, 'cookie_authentication', None) # using cookie authentication?
        if auth:
            user_name = request.get('login_name', None)
            password_empty = request.get('pwd_empty', None)=='1'
            ac_name = auth.name_cookie
            ac_password = auth.pw_cookie

            if not user_name:
                # no user name
                state.setError(ac_name, _(u'Please enter your login name.'), 'login_name_required')
            if password_empty:
                state.setError(ac_password, _(u'Please enter your password.'), 'password_required')
            verify_login_name = context.portal_properties.site_properties.getProperty('verify_login_name', 0)
            if user_name and verify_login_name:
                # XXX mixing up username and loginname here
                if mt.getMemberById(user_name) is None:
                    state.setError(ac_name, _(u'Login name not found.'), 'login_name_not_found')
                elif not password_empty:
                    state.setError(ac_password, _(u'Password incorrect.'), 'password_incorrect')
        context.plone_utils.addPortalMessage(_(u'Login failed. Both login name and password are case sensitive, check that caps lock is not enabled.'), 'error')
        state.set(status='failure')
    else: # no javascript - do low tech login failure
        context.plone_utils.addPortalMessage(_(u'Login failed. Both login name and password are case sensitive, check that caps lock is not enabled.'), 'error')
        state.set(status='failure_page')

return state
