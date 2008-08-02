## Script (Python) "extract_date_compnents"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=date=None
##title=
##
# this script extracts %Y %m %d %H %M from a given date string

context.plone_log("The extract_date_components script is deprecated and will "
                  "be removed in Plone 4.0.")

from DateTime import DateTime
from ZODB.POSException import ConflictError

try:
    date = DateTime(date)
except ConflictError:
    raise
except: #Combination of string/instances can be raised. catch all.
    pass

try:
    day = date.strftime('%d');
except AttributeError:
    day = '00'

try:
    month = date.strftime('%m');
except AttributeError:
    month = '00'

try:
    year = date.strftime('%Y');
except AttributeError:
    year = '00'

try:
    hour = date.strftime('%H');
except AttributeError:
    hour = '00'

try:
    minute = date.strftime('%M');
except AttributeError:
    minute = '00'

try:
    ampm = date.strftime('%p');
except AttributeError:
    ampm = '00'

return {'year':year, 'month':month,
        'day':day, 'hour':hour,
        'minute':minute, 'ampm':ampm}
