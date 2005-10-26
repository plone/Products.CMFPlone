## Script (Python) "truncID.py $Revision$"
##parameters=objID, size
##title=return truncated objID
##
if len(objID) > size:
    return objID[:size] + '...'
else:
    return objID
