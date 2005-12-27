## Controller Python Script "editSynProperties"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=
##title=Edit Syndication Properties
##

from Products.CMFPlone import PloneMessageFactory as _

REQUEST=context.REQUEST
pSyn = context.portal_syndication
pSyn.editSyInformationProperties(context,
                                 REQUEST['updatePeriod'],
                                 REQUEST['updateFrequency'],
                                 REQUEST['updateBase'],
                                 REQUEST['max_items'],
                                 REQUEST)
from Products.CMFPlone.utils import transaction_note
transaction_note('Updated syndication properties for %s at %s' % (context.title_or_id(), context.absolute_url()))

context.plone_utils.addPortalMessage(_(u'Syndication properties updated.'))
return state
