## Script (Python) "getNextMonth"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=month, year
##title=Calendar Presentation Helper
##
context.plone_log("The getNextMonth script is deprecated and will be "
                  "removed in plone 3.5.  Use the getNextMonth method "
                  "of the @@calendar_view view instead.")

month=int(month)
year=int(year)

if month==12:
    month, year = 1, year + 1
else:
    month+=1

return DateTime(year, month, 1)
