## Script (Python) "editSynProperties"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Enable Syndication for a resource
##

REQUEST=context.REQUEST
pSyn = context.portal_syndication
pSyn.editSyInformationProperties(context, REQUEST['updatePeriod'], REQUEST['updateFrequency'], REQUEST['updateBase'], REQUEST['max_items'], REQUEST)

return ('success', context, {'portal_status_message':context.REQUEST.get('portal_status_message', 'Syndication properties updated.')})
