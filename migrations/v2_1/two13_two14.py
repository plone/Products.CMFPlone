from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.UnicodeSplitter import Splitter, CaseNormalizer
from Products.CMFPlone.migrations.v2_1.alphas import reindexCatalog, \
     indexMembersFolder


def two13_two14(portal):
    """2.1.3 -> 2.1.4
    """
    out = []
    removePloneCssFromRR(portal, out)
    turnOnValidateEmail(portal, out)

    # Repair plone_lexicon pipeline
    if fixupPloneLexicon(portal, out):
        reindexCatalog(portal, out)

        # FIXME: *Must* be called after reindexCatalog.
        # In tests, reindexing loses the folders for some reason.
        indexMembersFolder(portal, out)

    return out

def removePloneCssFromRR(portal, out):
    """Removes the redundant, deprecated, and failing plone.css from portal_css.
       It is a python script now and just calls portal_css itself."""
    css_reg = getToolByName(portal, 'portal_css', None)
    if css_reg is not None:
        stylesheet_ids = css_reg.getResourceIds()
        if 'plone.css' in stylesheet_ids:
            css_reg.unregisterResource('plone.css')
            out.append('Unregistered deprecated plone.css')

def fixupPloneLexicon(portal, out):
    """Updates the plone_lexicon pipeline with the new splitter
       and case normalizer.
    """
    catalog = getToolByName(portal, 'portal_catalog', None)
    if catalog is not None:
        if 'plone_lexicon' in catalog.objectIds():
            lexicon = catalog.plone_lexicon
            pipeline = list(lexicon._pipeline)
            if len(pipeline) >= 2:
                if (not isinstance(pipeline[0], Splitter) or
                    not isinstance(pipeline[1], CaseNormalizer)):
                    pipeline[0] = Splitter()
                    pipeline[1] = CaseNormalizer()
                    lexicon._pipeline = tuple(pipeline)
                    # Clear the lexicon
                    from BTrees.OIBTree import OIBTree
                    from BTrees.IOBTree import IOBTree
                    from BTrees.Length import Length
                    lexicon._wids = OIBTree()
                    lexicon._words = IOBTree()
                    lexicon.length = Length()
                    out.append('Updated plone_lexicon pipeline.')
                    return True
    return False

def turnOnValidateEmail(portal, out):
    """validate_email should be on by default."""
    if portal.hasProperty('validate_email'):
        portal.manage_changeProperties(validate_email=True)
        out.append('Turned on validate_email.')

