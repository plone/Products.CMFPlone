## Controller Python Script "editSynProperties"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Edit Syndication Properties
##
state = context.portal_form_controller.getState(script, is_validator=0)

REQUEST=context.REQUEST
pSyn = context.portal_syndication
pSyn.editSyInformationProperties(context,
                                 REQUEST['updatePeriod'],
                                 REQUEST['updateFrequency'],
                                 REQUEST['updateBase'],
                                 REQUEST['max_items'],
                                 REQUEST)

return state.set(portal_status_message='Syndication properties updated.')
