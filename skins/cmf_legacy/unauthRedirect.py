## Script (Python) "unauthRedirect.py $Revision: 1.3 $"
##parameters=
##title=clear browser cookie
##
REQUEST=context.REQUEST
REQUEST.RESPONSE.redirect( context.absolute_url())
