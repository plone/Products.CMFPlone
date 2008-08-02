##parameters=event

context.plone_log("The getEventString script is deprecated and will be "
                  "removed in Plone 4.0.")

from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode

start = event['start'] and ':'.join(event['start'].split(':')[:2]) or ''
end = event['end'] and ':'.join(event['end'].split(':')[:2]) or ''
title = safe_unicode(event['title']) or 'event'

if start and end:
    eventstring = "%s-%s %s" % (start, end, title)
elif start: # can assume not event['end']
    eventstring = "%s - %s" % (start, title)
elif event['end']: # can assume not event['start']
    eventstring = "%s - %s" % (title, end)
else: # can assume not event['start'] and not event['end']
    eventstring = title

return eventstring
