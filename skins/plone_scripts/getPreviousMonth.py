## Script (Python) "getPreviousMonth"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=month, year
##title=Calendar Presentation Helper
##

try: month=int(month)
except: pass
try: year=int(year)
except: pass

if month==0 or month==1:
    month, year = 12, year - 1
else:
    month-=1

return DateTime(str(month) + '/1/' + str(year))
