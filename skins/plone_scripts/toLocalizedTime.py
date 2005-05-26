## Script (Python) "toLocalizedTime"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=time=None, long_format=None
##title=
##
# The time parameter must be either a string that is suitable for
# initializing a DateTime or a DateTime object.
# Returns a localized string.

from DateTime.DateTime import DateTime

if isinstance(time, DateTime):
    time = time.rfc822()

tool = context.translation_service
return tool.localized_time(time, long_format, context, domain='plone')
