## Script (Python) "truncID.py $Revision$"
##parameters=objID, size
##title=return truncated objID
##
context.plone_log("The truncID script is deprecated and will be "
                  "removed in plone 3.5.")
if len(objID) > size:
    return objID[:size] + '...'
else:
    return objID
