## Script (Python) "collector_issue_comment_header.py"
##title=Form the header for a new comment entry in an issue
##bind container=container
##bind context=context
##parameters=type

"""Return text for the header of a new comment entry in an issue."""

from DateTime import DateTime
import string
user = context.REQUEST.AUTHENTICATED_USER

if string.lower(type) == "comment":
    # We number the comments (sequence_number is incremented by add_comment)
    lead = "<hr> " + type + " #" + str(context.sequence_number)
else:
    # ... but don't number the other entries.
    lead = type

return "%s by %s on %s ==>" % (lead, str(user), DateTime().aCommon())
                                
