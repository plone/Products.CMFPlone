## Script (Python) "standard_error_message"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=**kwargs
##title=Dispatches to relevant error view
##

## by default we handle everything in 1 PageTemplate.
#  you could easily check for the error_type and
#  dispatch to an appropriate PageTemplate.

error_type=kwargs.get('error_type', None)
error_message=kwargs.get('error_message', None)
error_log_url=kwargs.get('error_log_url', None)
error_tb=kwargs.get('error_tb', None)
error_traceback=kwargs.get('error_traceback', None)
error_value=kwargs.get('error_value', None)

error_page=None

error_page=context.default_error_message(error_type=error_type,
                                         error_message=error_message,
                                         error_tb=error_tb,
                                         error_value=error_value)

return error_page

