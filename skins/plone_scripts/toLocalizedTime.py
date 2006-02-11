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
context.plone_log("The toLocalizedTime script is deprecated and will be "
                  "removed in plone 3.5.  Use the method of the @@plone view,"
                  " or the method in the main_template globals.")

tool = context.translation_service
return tool.ulocalized_time(time, long_format, context, domain='plone')
