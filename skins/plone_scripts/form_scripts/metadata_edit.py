## Script (Python) "metadata_edit"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##title=Update Content Metadata
##parameters=allowDiscussion=None,title=None,subject=None,description=None,contributors=None,effective_date=None,expiration_date=None,format=None,language=None,rights=None

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

return context.portal_navigation.getNextRequestFor( context
                                            , script.getId()
                                            , 'success'
                                            , portal_status_message='Metadata changed.' )

