## Script (Python) "errorMessages"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Returns a set of error messages
##
messages = {}
messages['illegal_id'] = 'This is not a legal id.'
messages['id_exists'] = 'This id already exists.'
messages['error_exists'] = 'Please correct the indicated errors.'
return messages
