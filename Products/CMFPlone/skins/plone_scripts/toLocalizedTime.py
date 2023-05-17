## Script (Python) "toLocalizedTime"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=time=None, long_format=None, time_only=None
##title=

# The time parameter must be either a string that is suitable for
# initializing a DateTime or a DateTime object.
# Returns a localized string.
return context.restrictedTraverse("@@plone").toLocalizedTime(
    time, long_format, time_only
)
