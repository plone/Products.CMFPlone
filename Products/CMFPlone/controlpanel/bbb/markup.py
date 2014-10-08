from zope.component import getAdapter
from zope.site.hooks import getSite
from Products.CMFPlone.interfaces.siteroot import IPloneSiteRoot
from zope.component import adapts
from zope.interface import implements
from Products.CMFCore.utils import getToolByName

from Products.CMFPlone.interfaces import IMarkupSchema


class MarkupControlPanelAdapter(object):

    adapts(IPloneSiteRoot)
    implements(IMarkupSchema)

    def __init__(self, context):
        self.context = context
        self.portal = getSite()
        pprop = getToolByName(self.portal, 'portal_properties')
        self.pmembership = getToolByName(context, 'portal_membership')
        portal_url = getToolByName(context, 'portal_url')
        self.portal = portal_url.getPortalObject()
        self.context = pprop.site_properties
        self.site_properties = pprop.site_properties
        self.portal_transforms = getToolByName(
            self.portal,
            'portal_transforms'
        )

    def get_default_type(self):
        return self.site_properties.getProperty('default_contenttype')

    def set_default_type(self, value):
        self.site_properties.manage_changeProperties(default_contenttype=value)

    default_type = property(get_default_type, set_default_type)

    def get_allowed_types(self):
        allowable_types = self.portal_transforms.listAvailableTextInputs()
        forbidden_types = list(
            self.site_properties.getProperty('forbidden_contenttypes')
        )
        allowed_types = [
            type for type in allowable_types if type not in forbidden_types
        ]
        return allowed_types

    def set_allowed_types(self, value):
        # The menu pretends to be a whitelist, but we are storing a blacklist
        # so that new types are available by default. So, we inverse the list.
        allowable_types = self.portal_transforms.listAvailableTextInputs()
        forbidden_types = [t for t in allowable_types if t not in value]
        self.site_properties.manage_changeProperties(
            forbidden_contenttypes=tuple(forbidden_types)
        )
    allowed_types = property(get_allowed_types, set_allowed_types)