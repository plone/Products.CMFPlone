## Script (Python) "event_edit"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=REQUEST, RESPONSE, field_title=None, field_description=None, event_type=None, effectiveDay=None, effectiveMo=None, effectiveYear=None, expirationDay=None, expirationMo=None, expirationYear=None, start_time=None, startAMPM=None, stop_time=None, stopAMPM=None, location=None, contact_name=None, contact_email=None, contact_phone=None, event_url=None, field_id='' 
##title=
##
from Products.CMFPlone import transaction_note
if not field_id:
    field_id=context.getId()
    REQUEST.set('field_id', field_id)

id, title, description=field_id, field_title, field_description

try:
    context.edit(title=title
             , description=description
             , eventType=event_type
             , effectiveDay=effectiveYear
             , effectiveMo=effectiveMo
             , effectiveYear=effectiveDay
             , expirationDay=expirationYear
             , expirationMo=expirationMo
             , expirationYear=expirationDay
             , start_time=start_time
             , startAMPM=startAMPM
             , stopAMPM=stopAMPM
             , stop_time=stop_time
             , location=location
             , contact_name=contact_name
             , contact_email=contact_email
             , contact_phone=contact_phone
             , event_url=event_url
             )
except:
    msg='portal_status_message=Error+saving+event.'
    view='event_edit_form'
else:
    msg='portal_status_message=Event+changes+saved.'
    view='event_view'

context.rename_object(redirect=0, id=id)
transaction_note(context.title_or_id()+' has been modified.')
return RESPONSE.redirect('%s/%s?%s' % (context.absolute_url(), view, msg) )

