## Controller Python Script "metadata_edit"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##title=Update Content Metadata
##parameters=allowDiscussion=None,title=None,subject=None,description=None,contributors=None,effective_date=None,expiration_date=None,format=None,language=None,rights=None,predefined_subjects=None

from Products.CMFPlone.utils import transaction_note
from Products.CMFPlone import PloneMessageFactory as _

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

new_context = context.portal_factory.doCreate(context)

new_context.plone_utils.editMetadata(new_context,
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

transaction_note('Edited properties for %s at %s' % (new_context.title_or_id(), new_context.absolute_url()))

context.plone_utils.addPortalMessage(_(u'Content properties have been saved.'))
return state.set(context=new_context)
