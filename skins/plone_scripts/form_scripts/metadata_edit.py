## Script (Python) "metadata_edit"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##title=Update Content Metadata
##parameters=allowDiscussion=None,title=None,subject=None,description=None,contributors=None,effective_date=None,expiration_date=None,format=None,language=None,rights=None,predefined_subjects=None
if subject is None:
    subject = []
if predefined_subjects is None:
    predefined_subjects = []
elif not same_type(predefined_subjects, []):
    predefined_subjects=[predefined_subjects,]
subject=[ps for ps in predefined_subjects if ps]+[s for s in subject if s]

if not effective_date:
   effective_date='None'
if not expiration_date:
   expiration_date='None'

context.plone_utils.editMetadata(context,
                                 allowDiscussion=allowDiscussion,
                                 title=title,
                                 subject=subject,
                                 description=description,
                                 contributors=contributors,
                                 effective_date=effective_date,
                                 expiration_date=expiration_date,
                                 format=format,
                                 language=language,
                                 rights=rights)

return ( 'success'
       , context
       , { 'portal_status_message':context.REQUEST.get( 'portal_status_message'
                                                      , 'Content Properties have been saved.') } )
