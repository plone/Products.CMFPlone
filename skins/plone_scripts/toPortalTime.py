## Script (Python) "toPortalTime"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=time=None
##title=
##
#given a time string convert it into a DateTime and then format it appropariately
from DateTime import DateTime
format='%m/%d/%Y %I:%M %p'

if time is None:
    time=DateTime()

proper_format=DateTime().strftime(format)
if same_type(time, ''): #best effort
    try:
        proper_format=DateTime(str(time)).strftime(format)
    except:
        proper_format=time
elif isinstance(time, DateTime):
    proper_format=time.strftime(format)
else:
    proper_format=time

return proper_format

