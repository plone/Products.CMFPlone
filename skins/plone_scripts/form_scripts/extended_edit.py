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
title=REQUEST.get('title', REQUEST.get('field_title', context.Title()))
description=REQUEST.get('description', REQUEST.get('field_description', context.Description()))
subject=REQUEST.get('subject', REQUEST.get('field_subject', context.Subject()))
effective_date=REQUEST.get('effective_date', None)
expiration_date=REQUEST.get('expiration_date', None)

#use plone metadata_edit
if title or description or subject: 
    context.metadata_edit(title=title,
                          subject=subject, 
                          description=description, 
                          effective_date=effective_date, 
                          expiration_date=expiration_date, 
                          redirect=0)
#moved the id/filename renaming to the xxx_edit scripts
#use rename_object() script
