## Script (Python) "getPreviousMonth"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=day, month, year
##title=
##

from DateTime import DateTime

day=str(day)
month=str(month)
year=str(year)

begin=DateTime(month+'/'+day+'/'+year+' 12:00:00AM')
end=DateTime(month+'/'+day+'/'+year+' 11:59:59PM')

return (begin, end)

