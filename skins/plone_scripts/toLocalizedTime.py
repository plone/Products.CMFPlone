## Script (Python) "toLocalizedTime"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=time=None, long_format=None
##title=
##
#given a time string convert it into a DateTime and then format it appropriately
#use time format of translation service

# get tool
tool = context.translation_service

return tool.localized_time(time, long_format, context, domain='plone')
