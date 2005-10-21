## Script (Python) "errorMessages"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Returns a set of error messages
##

from Products.CMFPlone import PloneMessageFactory as _

messages = {}
messages['illegal_id'] = _(u'This is not a legal id.')
messages['id_exists'] = _(u'This id already exists.')
messages['error_exists'] = _(u'Please correct the indicated errors.')
return messages
