## Script (Python) "reconfig"
##title=Reconfigure Portal
##parameters=

errors = context.portal_form_validation.validate(context, 'validate_reconfig')
if errors:
    edit_form=context.portal_navigation.getNextPageFor( context
                                                      , script.getId()
                                                      , 'failure' )
    return edit_form()
    
REQUEST=context.REQUEST
context.portal_properties.editProperties(REQUEST)
default_skin=context.portal_skins.getDefaultSkin()
context.plone_utils.setDefaultSkin(REQUEST.get('default_skin', default_skin))

return context.portal_navigation.getNextRequestFor( context
                                                  , script.getId()
                                                  , 'success'
                                                  , portal_status_message='CMF Settings changed.' )
