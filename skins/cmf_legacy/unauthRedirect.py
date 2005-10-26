## Script (Python) "unauthRedirect.py $Revision$"
##parameters=
##title=clear browser cookie
##
REQUEST=context.REQUEST
REQUEST.RESPONSE.redirect( context.absolute_url())
