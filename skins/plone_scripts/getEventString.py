##parameters=event

start = event['start'] and ':'.join(event['start'].split(':')[:2]) or ''
end = event['end'] and ':'.join(event['end'].split(':')[:2]) or ''
title = event['title'] or "something"

if start and end:
    eventstring = "%s-%s %s" % (start, end, title)
elif start: # can assume not event['end']
    eventstring = "%s - %s" % (start, title)
elif event['end']: # can assume not event['start']
    eventstring = "%s - %s" % (title, end)
else: # can assume not event['start'] and not event['end']
    eventstring = title

return eventstring
