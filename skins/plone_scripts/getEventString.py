##parameters=event

if event['start'] and event['end']:
    eventstring = "%s-%s %s" % (event['start'], event['end'], event['title'])
elif event['start']: # can assume not event['end']
    eventstring = "%s - %s" % (event['start'], event['title'] or "something")
elif event['end']: # can assume not event['start']
    eventstring = "%s - %s" % (event['title'], event['end'])
else: # can assume not event['start'] and not event['end']
    eventstring = event['title']

return eventstring
