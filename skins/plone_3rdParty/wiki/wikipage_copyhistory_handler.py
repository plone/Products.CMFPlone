## Script (Python) "wikipage_copyhistory_handler"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=REQUEST
##title=
##
keys = REQUEST['keys']
url = context.absolute_url()
context.history_copy_page_to_present(keys)
REQUEST.RESPONSE.redirect('%s' % url)