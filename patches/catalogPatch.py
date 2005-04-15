from DateTime import DateTime

APPLY_CEILING_DATE_PATCH = True     # Set to False for CMF 1.5
APPLY_SEARCH_RESULTS_PATCH = True

# This is the new ceiling date
CEILING_DATE = DateTime(2500, 0)    # 2499/12/31


# Patch 1
#
# Fixup the ceiling date in CMF 1.4 DublinCore
#
if APPLY_CEILING_DATE_PATCH:
    from Products.CatalogOptimizer.config import CEILING_DATE
    from Products.CMFDefault.DublinCore import DefaultDublinCoreImpl
    DefaultDublinCoreImpl._DefaultDublinCoreImpl__CEILING_DATE = CEILING_DATE


# Patch 2
#
# Change searchResults to use the effectiveRange index
#
# Note: It is important that we patch CMFCore here as LinguaPlone
# Pwnz0rz the searchResults method of the Plone catalog tool.
#
if APPLY_SEARCH_RESULTS_PATCH:
    from Products.CMFCore.CMFCorePermissions import AccessInactivePortalContent
    from Products.CMFCore.CatalogTool import CatalogTool
    from Products.CMFCore.utils import _getAuthenticatedUser
    from Products.CMFCore.utils import _checkPermission
    from Products.ZCatalog.ZCatalog import ZCatalog
    from DateTime import DateTime

    def searchResults(self, REQUEST=None, **kw):
        """ Calls ZCatalog.searchResults with extra arguments that
            limit the results to what the user is allowed to see.

            This version uses the 'effectiveRange' DateRangeIndex.
        """
        user = _getAuthenticatedUser(self)
        kw['allowedRolesAndUsers'] = self._listAllowedRolesAndUsers(user)

        if not _checkPermission(AccessInactivePortalContent, self):
            kw['effectiveRange'] = DateTime()
            if kw.has_key('effective'):
                del kw['effective']
            if kw.has_key('expires'):
                del kw['expires']

        return ZCatalog.searchResults(self, REQUEST, **kw)

    CatalogTool.searchResults = searchResults
    CatalogTool.__call__ = searchResults

