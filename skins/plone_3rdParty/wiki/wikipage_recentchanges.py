## Script (Python) "wikipage_recentchanges"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
context.REQUEST['RESPONSE'].redirect(
   '%s/wiki_recentchanges' % context.aq_parent.absolute_url() )