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
from Products.CMFPlone.PloneUtilities import translate_wrapper 
from DateTime import DateTime 
import string

if not time:
   return None

if long_format:
   msgid = 'date_format_long'
else:
   msgid = 'date_format_short'

localized_time = ''

# retrieve date format via translation service
dateFormat = translate_wrapper('plone', msgid, context = context) 
if dateFormat == None or dateFormat == '':
   # fallback to portal_properties if no msgstr received from translation service
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

# extract parts from date
try:
    time = DateTime(time)
except:
    pass

# extract date parts from DateTime object
dateParts = time.parts()
day = '%02d' % dateParts[2]
month = '%02d' % dateParts[1]
year = dateParts[0]
hour = '%02d' % dateParts[3]
minute = '%02d' % dateParts[4]

# substitute variables with actual values 
localized_time = string.replace(dateFormat, '${DAY}', str(day)) 
localized_time = string.replace(localized_time, '${MONTH}', str(month)) 
localized_time = string.replace(localized_time, '${YEAR}', str(year)) 
localized_time = string.replace(localized_time, '${HOUR}', str(hour)) 
localized_time = string.replace(localized_time, '${MINUTE}', str(minute))

return localized_time

