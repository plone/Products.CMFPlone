## Script (Python) "toPortalTime"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=time=None, long_format=None
##title=
##
#given a time string convert it into a DateTime and then format it appropariately
from DateTime import DateTime
localized_time=None
now=DateTime()
properties=context.portal_properties.site_properties

if long_format:
    format=properties.localLongTimeFormat
else:
    format=properties.localTimeFormat

if not time:
    time=DateTime().pCommon()

try:
    localized_time=DateTime(str(time)).strftime(format)
except IndexError:
    pass 

return localized_time

