## Script (Python) "getBeginAndEndTimes"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=day, month, year
##title=
##

day=int(day)
month=int(month)
year=int(year)

begin=DateTime('%d-%02d-%02d 00:00:00' % (year, month, day))
end=DateTime('%d-%02d-%02d 23:59:59' % (year, month, day))

return (begin, end)
