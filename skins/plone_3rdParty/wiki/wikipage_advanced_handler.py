## Script (Python) "wikipage_advanced_handler"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=REQUEST
##title=
##
context.setRegulations(d=REQUEST)

REQUEST.RESPONSE.redirect('%s?portal_status_message=Advanced+actions+updated.'
                         % context.absolute_url())