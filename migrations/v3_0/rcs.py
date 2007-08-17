from Products.CMFPlone.migrations.migration_util import loadMigrationProfile

from Products.MimetypesRegistry.mime_types.mtr_mimetypes import text_web_intelligent
from types import InstanceType
from Products.PortalTransforms.transforms.web_intelligent_plain_text_to_html import register as intel2html_register
from Products.PortalTransforms.transforms.html_to_web_intelligent_plain_text import register as html2intel_register


def rc1_rc2(portal):
    """ 3.0-rc1 -> 3.0-rc2
    """

    out = []

    addIntelligentText(portal, out)

    return out

def rc2_final(portal):
    
    out = []
    
    loadMigrationProfile(portal, 'profile-Products.CMFPlone.migrations:3.0rc2-3.0final')
    
    return out

def addIntelligentText(portal, out):
    """ add intelligenttext mime type and transforms that have been
    introduced in MimetypesRegistry and PortalTransforms 1.6 and that
    are never updated anywhere (#6684)
    """
    # Add mime type
    # See MimetypesRegistry/mime_types/mtr_mimetypes.py
    mt = text_web_intelligent
    if type(mt) != InstanceType:
        mt = mt()
    portal.mimetypes_registry.register(mt)
    out.append("Added text_web_intelligent mime type to registry")

    # Add transforms
    # See PortalTransforms/transforms/__init__.py
    engine = portal.portal_transforms
    engine.registerTransform(intel2html_register())
    out.append("Added intelligenttext to html transform to registry")
    engine.registerTransform(html2intel_register())
    out.append("Added html to intelligenttext transform to registry")
