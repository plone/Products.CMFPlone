## Script (Python) "extended_edit"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=redirect=1
##title=after xxx_edit hook
##
#ideally we will always be in the same context when we use this.  
#this will go after any edit action, i.e. document_edit
#change metadata if its changed

REQUEST=context.REQUEST
title=REQUEST.get('title', REQUEST.get('field_title', ''))
description=REQUEST.get('description', REQUEST.get('field_description', ''))
subject=REQUEST.get('subject', REQUEST.get('field_subject')context.Subject()))
effective_date=REQUEST.get('effective_date', None)
expiration_date=REQUEST.get('expiration_date', None)

if title or description or subject: #we dont want metadata to redirect (uses modified metadata_edit)
    context.metadata_edit(title=title, subject=subject, description=description, effective_date=effective_date, expiration_date=expiration_date, redirect=0)


#if a new_id 
if REQUEST['id']:
    if REQUEST['id']!=context.getId():
        context.manage_renameObjects( (context.getId(), ), (REQUEST['id'], ), REQUEST)
        if redirect:
            status_msg=REQUEST.get('portal_status_message', 'Changes+have+been+Saved.')
            url='%s/%s?%s' % ( REQUEST['URL2']
                             , REQUEST['id']
                             , 'portal_status_message='+status_msg )
            return REQUEST.RESPONSE.redirect(url)

