##parameters=event
from Products.CMFCore.utils import getToolByName

plone_utils = getToolByName(context, 'plone_utils')
encoding = plone_utils.getSiteEncoding()

start = event['start'] and ':'.join(event['start'].split(':')[:2]) or ''
end = event['end'] and ':'.join(event['end'].split(':')[:2]) or ''
title = unicode(event['title'], encoding) or 'event'

if start and end:
    eventstring = "%s-%s %s" % (start, end, title)
elif start: # can assume not event['end']
    eventstring = "%s - %s" % (start, title)
elif event['end']: # can assume not event['start']
    eventstring = "%s - %s" % (title, end)
else: # can assume not event['start'] and not event['end']
    eventstring = title

return eventstring
