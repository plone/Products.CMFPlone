from Products.PageTemplates.PageTemplateFile import PageTemplateFile

from Products.CMFCore.utils import getToolByName
from Products.GenericSetup.tool import SetupTool
from Products.GenericSetup import profile_registry
from Products.GenericSetup import EXTENSION

from Portal import PloneSite
from utils import WWW_DIR
from interfaces import IPloneSiteRoot

_TOOL_ID = 'portal_setup'


def addPloneSiteForm(dispatcher):
    """
    Wrap the PTF in 'dispatcher'.
    """
    wrapped = PageTemplateFile('addSite', WWW_DIR).__of__(dispatcher)

    extension_profiles = []
    for info in profile_registry.listProfileInfo():
        if info.get('type') == EXTENSION and \
           info.get('for') in (IPloneSiteRoot, None):
            extension_profiles.append(info)
    
    return wrapped(extension_profiles=tuple(extension_profiles))

def addPloneSite(dispatcher, id, title='', description='',
                 create_userfolder=1, email_from_address='',
                 email_from_name='', validate_email=0,
                 profile_id='CMFPlone:plone', snapshot=False,
                 RESPONSE=None, extension_ids=()):
    """ Add a PloneSite to 'dispatcher', configured according to 'profile_id'.
    """
    site = PloneSite(id)
    dispatcher._setObject(id, site)
    site = dispatcher._getOb(id)

    site._setObject(_TOOL_ID, SetupTool(_TOOL_ID))
    setup_tool = getToolByName(site, _TOOL_ID)

    setup_tool.setImportContext('profile-%s' % profile_id)
    setup_tool.runAllImportSteps()
    for extension_id in extension_ids:
        setup_tool.setImportContext('profile-%s' % extension_id)
        setup_tool.runAllImportSteps()
    setup_tool.setImportContext('profile-%s' % profile_id)

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
