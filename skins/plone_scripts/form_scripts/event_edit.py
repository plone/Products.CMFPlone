## Script (Python) "event_edit"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=REQUEST, RESPONSE, field_title=None, field_description=None, event_type=None, start_date=None, end_date=None, location=None, contact_name=None, contact_email=None, contact_phone=None, event_url=None, field_id='' 
##title=
##

# need to parse date string *before* passing to Event.edit since
# it expects bite sized chunks....
from DateTime import DateTime

dt_start = DateTime( start_date )
dt_end = DateTime( end_date )

try:
    context.edit(title=field_title
             , description=field_description
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
                               , id=field_id
                               , description=field_description)

except:
    msg='portal_status_message=Error+saving+event.'
    view='event_edit_form'
else:
    msg='portal_status_message=Event+changes+saved.'
    view='event_view'

return RESPONSE.redirect('%s/%s?%s' % (context.absolute_url(),
                                       view, msg) )

