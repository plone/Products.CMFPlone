## Script (Python) "clearCookie.py $Revision$"
##parameters=
##title=clear browser cookie
##
context.plone_log("The clearCookie script is deprecated and will be "
                  "removed in plone 3.5.")
REQUEST=context.REQUEST
REQUEST.RESPONSE.expireCookie('folderfilter', path='/')
REQUEST.RESPONSE.redirect( context.absolute_url() + '/folder_contents?portal_status_message=Filter+cleared.')
