## Script (Python) "setProperties"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=keep_entries,copy_to_zlog,ignored_exceptions
##title=
##
request=context.REQUEST

results = context.error_log.setProperties(keep_entries,copy_to_zlog,ignored_exceptions)
return request.RESPONSE.redirect(context.absolute_url() +'/prefs_error_log_form?portal_status_message=%s' % ('Data+Updated'))
