## Script (Python) "unauthRedirect.py $Revision$"
##parameters=
##title=clear browser cookie
##
context.plone_log("The unauthRedirect script is deprecated and will be "
                  "removed in plone 3.5.")
REQUEST=context.REQUEST
REQUEST.RESPONSE.redirect( context.absolute_url())
