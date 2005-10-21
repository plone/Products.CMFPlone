## Script (Python) "prefs_error_log_setProperties"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=keep_entries,ignored_exceptions,copy_to_zlog=0
##title=
##

from Products.CMFPlone import PloneMessageFactory as _
from Products.PythonScripts.standard import url_quote_plus

request=context.REQUEST

context.error_log.setProperties(keep_entries,copy_to_zlog,ignored_exceptions)

msg = _(u'Data updated.'')
return request.RESPONSE.redirect(context.absolute_url() +
            '/prefs_error_log_form?portal_status_message=%s' % url_quote_plus(msg))
