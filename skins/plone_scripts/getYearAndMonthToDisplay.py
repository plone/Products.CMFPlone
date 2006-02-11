##parameters=
##title=Calendar Presentation Helper
context.plone_log("The getYearAndMonthToDisplay script is deprecated and will be "
                  "removed in plone 3.5.  Use the getYearAndMonthToDisplay method "
                  "of the @@calendar_view view instead.")

# Returns the year and month that the calendar portlet should display.
# If uses_session is true stores the values in the session.

current = DateTime()
request = context.REQUEST
session = None

# First priority goes to the data in the REQUEST
year = request.get('year', None)
month = request.get('month', None)

# Next get the data from the SESSION
if container.portal_calendar.getUseSession():
    session = request.get('SESSION', None)
    if session:
        if not year:
            year = session.get('calendar_year', None)
        if not month:  
            month = session.get('calendar_month', None)

# Last resort to today
if not year:   
    year = current.year()
if not month:  
    month = current.month()

year, month = int(year), int(month)

# Store the results in the session for next time
if session:
    session.set('calendar_year', year)
    session.set('calendar_month', month)

# Finally return the results
return year, month
