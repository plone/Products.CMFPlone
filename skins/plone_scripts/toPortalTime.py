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
if not long_format:
    format=context.portal_properties.localTimeFormat
else:
    format=context.portal_properties.localLongTimeFormat
portal_time=None
if time is None: 
    time=DateTime()
try:
    portal_time=DateTime(str(time)).strftime(format)
except:
    portal_time=time
return portal_time
