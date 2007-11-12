from Products.CMFCore.ActionInformation import Action
from Products.CMFCore.permissions import DeleteObjects
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.UnicodeSplitter import Splitter, CaseNormalizer

from Products.CMFPlone.migrations.migration_util import loadMigrationProfile
from Products.CMFPlone.migrations.v3_0.alphas import migrateOldActions
from Products.CMFPlone.migrations.v3_0.alphas import enableZope3Site
from Products.CMFPlone.migrations.v3_0.alphas import registerToolsAsUtilities


def final_two51(portal):
    """2.5-final -> 2.5.1
    """
    out = []

    # Make the portal a Zope3 site
    enableZope3Site(portal, out)

    # register some tools as utilities
    registerToolsAsUtilities(portal, out)

    # We need to migrate all existing actions to new-style actions first
    migrateOldActions(portal, out)

    loadMigrationProfile(portal, 'profile-Products.CMFPlone.migrations:2.5final-2.5.1')

    # Repair plone_lexicon pipeline
    fixupPloneLexicon(portal, out)

    # Required for #5569 (is_folderish needs reindexing) and #5231 (all text
    # indices need to be reindexed so they are split properly)
    migtool = getToolByName(portal, 'portal_migration')
    migtool._needRecatalog = True

    return out


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
