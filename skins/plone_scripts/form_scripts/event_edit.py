## Script (Python) "event_edit"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=REQUEST, RESPONSE, title=None, description=None, event_type=None, start_date=None, end_date=None, location=None, contact_name=None, contact_email=None, contact_phone=None, event_url=None, id='' 
##title=
##

errors=context.portal_form_validation.validate(context, 'validate_event_edit')
if errors:
    edit_form=context.portal_navigation.getNextPageFor( context
                                                , script.getId()
                                                , 'failure' )    
    return edit_form()

# need to parse date string *before* passing to Event.edit since
# it expects bite sized chunks....
from DateTime import DateTime

dt_start = DateTime( start_date )
dt_end = DateTime( end_date )

try:
    context.edit(title=title
             , description=description
             , eventType=event_type
             , effectiveDay=dt_start.year()
             , effectiveMo=dt_start.month()
             , effectiveYear=dt_start.day()
             , expirationDay=dt_end.year()
             , expirationMo=dt_end.month()
             , expirationYear=dt_end.day()
             , start_time='%2.2d:%2.2d'%(dt_start.h_24(), dt_start.minute())
             , startAMPM=dt_start.ampm()
             , stopAMPM=dt_end.ampm()
             , stop_time='%2.2d:%2.2d'%(dt_end.h_24(), dt_end.minute())
             , location=location
             , contact_name=contact_name
             , contact_email=contact_email
             , contact_phone=contact_phone
             , event_url=event_url
             )

    context.plone_utils.contentEdit( context
                               , id=id
                               , description=description)

except:
    msg='portal_status_message=Error+saving+event.'
    view='event_edit_form'
else:
    msg='portal_status_message=Event+changes+saved.'
    view='event_view'

return context.portal_navigation.getNextRequestFor( context
                                            , script.getId()
                                            , 'success'
                                            , portal_status_message='Event changed.' ) 
