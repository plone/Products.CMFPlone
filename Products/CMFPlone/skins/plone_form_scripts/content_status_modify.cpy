## Controller Python Script "content_status_modify"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=workflow_action=None, comment='', effective_date=None, expiration_date=None, *args
##title=handles the workflow transitions of objects
##
from ZODB.POSException import ConflictError
from DateTime import DateTime
from Products.CMFPlone.utils import transaction_note
from Products.CMFPlone import PloneMessageFactory as _
from AccessControl import Unauthorized
from Products.CMFCore.utils import getToolByName

plone_utils = getToolByName(context, 'plone_utils')
contentEditSuccess=0
plone_log=context.plone_log
new_context = context.portal_factory.doCreate(context)
portal_workflow=new_context.portal_workflow
transitions = portal_workflow.getTransitionsFor(new_context)
transition_ids = [t['id'] for t in transitions]

if workflow_action in transition_ids and not effective_date and context.EffectiveDate()=='None':
    effective_date=DateTime()

def editContent(obj, effective, expiry):
    kwargs = {}
    if effective and (isinstance(effective, DateTime) or len(effective) > 5): # may contain the year
        kwargs['effective_date'] = effective
    if expiry and (isinstance(expiry, DateTime) or len(expiry) > 5): # may contain the year
        kwargs['expiration_date'] = expiry
    new_context.plone_utils.contentEdit( obj, **kwargs)

#You can transition content but not have the permission to ModifyPortalContent
try:
    editContent(new_context,effective_date,expiration_date)
    contentEditSuccess=1
except Unauthorized:
    pass

wfcontext = context

# Create the note while we still have access to wfcontext
note = 'Changed status of %s at %s' % (wfcontext.title_or_id(), wfcontext.absolute_url())

if workflow_action in transition_ids:
    wfcontext=new_context.portal_workflow.doActionFor( context,
                                                       workflow_action,
                                                       comment=comment )

if not wfcontext:
    wfcontext = new_context

#The object post-transition could now have ModifyPortalContent permission.
if not contentEditSuccess:
    try:
        editContent(wfcontext, effective_date, expiration_date)
    except Unauthorized:
        pass

transaction_note(note)

# If this item is the default page in its parent, attempt to publish that
# too. It may not be possible, of course
if plone_utils.isDefaultPage(new_context):
    parent = new_context.aq_inner.aq_parent
    try:
        parent.content_status_modify( workflow_action,
                                      comment,
                                      effective_date=effective_date,
                                      expiration_date=expiration_date )
    except ConflictError:
        raise
    except Exception:
        pass

context.plone_utils.addPortalMessage(_(u'Item state changed.'))
return state.set(context=wfcontext)
