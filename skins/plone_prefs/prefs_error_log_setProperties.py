## Script (Python) "setProperties"
##
request=context.REQUEST

results = context.error_log.setProperties(keep_entries,copy_to_zlog,ignored_exceptions)
return request.RESPONSE.redirect(context.absolute_url() +'/prefs_error_log_form?portal_status_message=%s' % ('Data+Updated'))