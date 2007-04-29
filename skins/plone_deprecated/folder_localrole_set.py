## Script (Python) "folder_localrole_set"
##parameters=use_acquisition=0
##title=set acquitision
##

from Products.CMFPlone.utils import transaction_note
from Products.CMFPlone import PloneMessageFactory as _

putils = context.plone_utils
putils.acquireLocalRoles(context, use_acquisition, REQUEST=context.REQUEST)
if use_acquisition:
    msg=_(u'Role Acquisition is now turned on.')
else:
    msg=_(u'Role Acquisition is now turned off.')

transaction_note('Modified acquisition settings for folder %s at %s' % (context.title_or_id(), context.absolute_url()))
context.plone_utils.addPortalMessage(msg)

context.REQUEST.RESPONSE.redirect(context.absolute_url() + '/folder_localrole_form')
