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

try:
  date = DateTime(date)
except:
  pass

try:
  day = date.strftime('%d');
except:
  day = '00'
try:
  month = date.strftime('%m');
except:
  month = '00'
try:
  year = date.strftime('%Y');
except:
  year = '00'

try:
  hour = date.strftime('%H');
except:
  hour = '00'
  
try:
  minute = date.strftime('%M');
except:
  minute = '00'

try:
  ampm = date.strftime('%p');
except:
  ampm = '00'

return {'year':year,'month':month,'day':day, 'hour':hour, 'minute':minute, 'ampm':ampm}