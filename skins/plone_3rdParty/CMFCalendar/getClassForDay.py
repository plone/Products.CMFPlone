##parameters=day

# pythonscript getClassForDay(day)
# day is a mapping eg {'day':12, 'url':None, 'event':None}
# day is 0 ==> overlapped previous or next month
# returns the appropriate css class name for a day

if day['event']:
    return 'events'
if not day['day']:
    return 'othermonth'
return ''
