from zope.component import getAllUtilitiesRegisteredFor
from zope.interface import implements

from Products.GenericSetup.interfaces import ISetupTool
from Products.GenericSetup.tool import SetupTool
from Products.GenericSetup import profile_registry
from Products.GenericSetup import BASE, EXTENSION
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

from Portal import PloneSite
from utils import WWW_DIR
from interfaces import INonInstallable
from interfaces import IPloneSiteRoot

_TOOL_ID = 'portal_setup'
_DEFAULT_PROFILE = 'Products.CMFPlone:plone'


class HiddenProfiles(object):
    implements(INonInstallable)

    def getNonInstallableProfiles(self):
        return [u'Products.Archetypes:Archetypes',
                u'Products.CMFDiffTool:CMFDiffTool',
                u'Products.CMFEditions:CMFEditions',
                u'Products.CMFFormController:CMFFormController',
                u'Products.CMFQuickInstallerTool:CMFQuickInstallerTool',
                u'Products.MimetypesRegistry:MimetypesRegistry',
                u'Products.PortalTransforms:PortalTransforms',
                u'Products.PloneLanguageTool:PloneLanguageTool',
                u'Products.PlonePAS:PlonePAS',
                u'plone.browserlayer:default',
                u'plone.portlet.static:default',
                u'plone.portlet.collection:default',
                u'kupu:default',
                u'Products.CMFPlone:dependencies',
                ]


def addPloneSiteForm(dispatcher):
    """
    Wrap the PTF in 'dispatcher'.
    """
    wrapped = PageTemplateFile('addSite', WWW_DIR).__of__(dispatcher)

    base_profiles = []
    extension_profiles = []
    not_installable = []

    utils = getAllUtilitiesRegisteredFor(INonInstallable)
    for util in utils:
        not_installable.extend(util.getNonInstallableProfiles())

    for info in profile_registry.listProfileInfo():
        if info.get('type') == EXTENSION and \
           info.get('for') in (IPloneSiteRoot, None):
            if info.get('id') not in not_installable:
                extension_profiles.append(info)

    for info in profile_registry.listProfileInfo():
        if info.get('type') == BASE and \
           info.get('for') in (IPloneSiteRoot, None):
            if info.get('id') not in not_installable:
                base_profiles.append(info)

    return wrapped(base_profiles=tuple(base_profiles),
                   extension_profiles=tuple(extension_profiles),
                   default_profile=_DEFAULT_PROFILE)

def addPloneSite(dispatcher, id, title='', description='',
                 create_userfolder=1, email_from_address='',
                 email_from_name='', validate_email=0,
                 profile_id=_DEFAULT_PROFILE, snapshot=False,
                 RESPONSE=None, extension_ids=()):
    """ Add a PloneSite to 'dispatcher', configured according to 'profile_id'.
    """
    site = PloneSite(id)
    dispatcher._setObject(id, site)
    site = dispatcher._getOb(id)

    site._setObject(_TOOL_ID, SetupTool(_TOOL_ID))
    setup_tool = getattr(site, _TOOL_ID)

    setup_tool.setBaselineContext('profile-%s' % profile_id)
    setup_tool.runAllImportStepsFromProfile('profile-%s' % profile_id)
    for extension_id in extension_ids:
        setup_tool.runAllImportStepsFromProfile('profile-%s' % extension_id)

    props = {}
    prop_keys = ['title', 'description', 'email_from_address',
                 'email_from_name', 'validate_email']
    loc_dict = locals()
    for key in prop_keys:
        if loc_dict[key]:
            props[key] = loc_dict[key]
    if props:
        site.manage_changeProperties(**props)

    if snapshot is True:
        setup_tool.createSnapshot('initial_configuration')

    if RESPONSE is not None:
        RESPONSE.redirect('%s/manage_main?update_menu=1'
                         % dispatcher.absolute_url())
