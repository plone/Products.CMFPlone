## Script (Python) "truncID.py $Revision: 1.3 $"
##parameters=objID, size
##title=return truncated objID
##
if len(objID) > size:
    return objID[:size] + '...'
else:
    return objID
