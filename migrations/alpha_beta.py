# alpha Plones to migrate tooling to a new site.
# Its rather unfortunate that its a destructive process.
# To overcome this will require us being very careful about
# releasing stuff to public and promoting 'the one way' of doing things

from Products.CMFCore.DirectoryView import createDirectoryView 
from Products.CMFPlone import cmfplone_globals
from Products.CMFPlone.Portal import PloneGenerator
from Products.CMFPlone.CustomizationPolicy import DefaultCustomizationPolicy

def bestEffortDirectoryViews(ob, name, _prefix):
    '''
    Adds a directory view for every subdirectory of the
    given directory.
    '''
    from types import StringType
    from os import path, listdir, stat
    from Globals import HTMLFile, Persistent, package_home, DTMLFile
    from Products.CMFCore.utils import expandpath, minimalpath
    from Products.CMFCore.DirectoryView import _dirreg
    # Meant to be called by filesystem-based code.
    # Note that registerDirectory() still needs to be called
    # by product initialization code to satisfy
    # persistence demands.
    if not isinstance(_prefix, StringType):
        _prefix = package_home(_prefix)
    fp = path.join(_prefix, name)
    filepath = minimalpath(fp)
    info = _dirreg.getDirectoryInfo(filepath)
    if info is None:
        raise ValueError('Not a registered directory: %s' % filepath)
    for entry in info.getSubdirs():
        filepath2 = path.join(filepath, entry)
        try:
            createDirectoryView(ob, filepath2, entry)
        except:
            pass

def kidgloves(skintool):
    """ treat the skintool with care
        We will register paths that need registering.
        We then will prune skinpaths.
    """
    skins=skintool.selections
    rm_ids=('plone_calendar', 'plone_ie')
    add_ids=('plone_ecmascript', 'plone_3rdParty/CMFCalendar')
    for skinname in skins.keys():
        skinpaths=skins[skinname]
        paths=[elem.strip() for elem in skinpaths.split(',') if elem.strip() not in rm_ids]
        for id in add_ids:
            paths.insert(paths.index('custom'), id)
        skins[skinname]=','.join(paths)
    
def migrate(portal):
    addPloneTool=portal.manage_addProduct['CMFPlone'].manage_addTool
    addCoreTool=portal.manage_addProduct['CMFCore'].manage_addTool
    addDefaultTool=portal.manage_addProduct['CMFDefault'].manage_addTool

    rm_ids=('portal_form_validation', 'plone_utils', 'portal_navigation',
            'portal_migration')
    for id in rm_ids:
        if id in portal.objectIds():
            portal.manage_delObjects(id)

    if 'portal_registration' not in portal.objectIds():
        addDefaultTool('Default Registration Tool')
    
    base_config=PloneGenerator()
    base_config.customizePortalOptions(portal)
    base_config.setupPloneWorkflow(portal)
    base_config.setupForms(portal)

    sk_tool=portal.portal_skins
    bestEffortDirectoryViews( sk_tool, 'skins', cmfplone_globals )
    kidgloves(sk_tool)

    custom=DefaultCustomizationPolicy()
    custom.customize(portal)
    return 'fin'

