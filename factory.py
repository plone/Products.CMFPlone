from Products.PageTemplates.PageTemplateFile import PageTemplateFile

from Products.CMFCore.utils import getToolByName
from Products.GenericSetup import EXTENSION
from Products.GenericSetup import profile_registry
from Products.GenericSetup.tool import SetupTool

from Portal import PloneSite
from utils import WWW_DIR
_TOOL_ID = 'portal_setup'


def addPloneSiteForm(dispatcher):
    """
    Wrap the PTF in 'dispatcher'.

    XXX improve addSite.zpt to handle alternate base and extension policies,
        provided by this method.  (need to only show Plone-specific ones.)
    """
    wrapped = PageTemplateFile('addSite', WWW_DIR).__of__(dispatcher)
    return wrapped()

def addPloneSite(dispatcher, id, title='', description='',
                 create_userfolder=1, email_from_address='',
                 email_from_name='', validate_email=0,
                 profile_id='CMFPlone:plone', snapshot=True,
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
