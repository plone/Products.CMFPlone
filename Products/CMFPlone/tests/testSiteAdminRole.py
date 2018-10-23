# -*- coding: utf-8 -*-
from AccessControl.PermissionRole import rolesForPermissionOn
from Products.CMFPlone.testing import PRODUCTS_CMFPLONE_INTEGRATION_TESTING

import unittest


class TestSiteAdministratorRole(unittest.TestCase):

    layer = PRODUCTS_CMFPLONE_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']

    def testExpectedPermissions(self):
        # This integration test shows that the correct permissions were
        # assigned to the Site Administrator role (whether inherited from the
        # Zope application, or specified in the portal rolemap).
        expected = {
            'Access contents information':                              1,
            'Access inactive portal content':                           1,
            'Add ATContentTypes tools':                                 0,
            'Add Accelerated HTTP Cache Managers':                      0,
            'Add Archetypes Tools':                                     0,
            'Add BTreeFolder2s':                                        0,
            'Add Browser Id Manager':                                   0,
            'Add CMF Action Icons Tools':                               0,
            'Add CMF Caching Policy Managers':                          0,
            'Add CMF Calendar Tools':                                   0,
            'Add CMF Core Tools':                                       0,
            'Add CMF Default Tools':                                    0,
            'Add CMF Diff Tools':                                       0,
            'Add CMF Editions Tools':                                   0,
            'Add CMF Placeful Workflow Tools':                          0,
            'Add CMF QuickInstaller Tools':                             0,
            'Add CMF Sites':                                            0,
            'Add CMF Unique Id Tools':                                  0,
            'Add CMFQuickInstallerTools':                               0,
            'Add Content Type Registrys':                               0,
            'Add Controller Page Templates':                            0,
            'Add Controller Python Scripts':                            0,
            'Add Controller Validators':                                0,
            'Add Cookie Crumblers':                                     0,
            'Add Database Methods':                                     0,
            'Add Documents, Images, and Files':                         0,
            'Add External Methods':                                     0,
            'Add Filesystem Directory Views':                           0,
            'Add Folders':                                              0,
            'Add Form Controller Tools':                                0,
            'Add Generic Setup Tools':                                  0,
            'Add Groups':                                               0,
            'Add MailHost objects':                                     0,
            'Add Marshaller Predicate':                                 0,
            'Add Marshaller Registry':                                  0,
            'Add MimetypesRegistry Tools':                              0,
            'Add Page Templates':                                       0,
            'Add Password Reset Tools':                                 0,
            'Add Placeful Workflow Tools':                              0,
            'Add Plone Language Tools':                                 0,
            'Add Plone Tools':                                          0,
            'Add PlonePAS Tools':                                       0,
            'Add Pluggable Index':                                      0,
            'Add Plugin Registrys':                                     0,
            'Add PortalTransforms Tools':                               0,
            'Add Python Scripts':                                       0,
            'Add RAM Cache Managers':                                   0,
            'Add ReStructuredText Documents':                           0,
            'Add Repositories':                                         0,
            'Add ResourceRegistries Tools':                             0,
            'Add Session Data Manager':                                 0,
            'Add Site Roots':                                           0,
            'Add Temporary Folder':                                     0,
            'Add TinyMCE Tools':                                        0,
            'Add Transient Object Container':                           0,
            'Add User Folders':                                         0,
            'Add Virtual Host Monsters':                                0,
            'Add Vocabularies':                                         0,
            'Add Workflow Policy':                                      0,
            'Add ZCatalogs':                                            0,
            'Add ZODB Mount Points':                                    0,
            'Add plone.app.customerizes':                               0,
            'Add portal content':                                       1,
            'Add portal events':                                        1,
            'Add portal folders':                                       1,
            'Add portal member':                                        1,
            'Add secure MailHost objects':                              0,
            'Allow sendto':                                             1,
            'Archetypes Tests: Protected Type View':                    0,
            'Archetypes Tests: Protected Type Write':                   0,
            'CMFEditions: Access previous versions':                    1,
            'CMFEditions: Apply version control':                       1,
            'CMFEditions: Checkout to location':                        1,
            'CMFEditions: Manage versioning policies':                  1,
            'CMFEditions: Purge version':                               1,
            'CMFEditions: Revert to previous versions':                 1,
            'CMFEditions: Save new version':                            1,
            'Change Browser Id Manager':                                0,
            'Change DTML Documents':                                    0,
            'Change DTML Methods':                                      0,
            'Change Database Methods':                                  0,
            'Change External Methods':                                  0,
            'Change Images and Files':                                  0,
            'Change Page Templates':                                    0,
            'Change Python Scripts':                                    0,
            'Change Session Data Manager':                              0,
            'Change bindings':                                          0,
            'Change cache managers':                                    0,
            'Change cache settings':                                    0,
            'Change configuration':                                     0,
            'Change local roles':                                       1,
            'Change permissions':                                       0,
            'Change proxy roles':                                       0,
            'Content rules: Manage rules':                              1,
            'Copy or Move':                                             1,
            'Create Transient Objects':                                 0,
            'Define permissions':                                       0,
            'Delete Groups':                                            0,
            'Delete objects':                                           1,
            'Edit ReStructuredText':                                    0,
            'FTP access':                                               1,
            'Five: Add TTW View Template':                              0,
            'Import/Export objects':                                    0,
            'List folder contents':                                     1,
            'List portal members':                                      1,
            'List undoable changes':                                    1,
            'Log Site Errors':                                          0,
            'Log to the Event Log':                                     0,
            'Mail forgotten password':                                  1,
            'Manage Access Rules':                                      0,
            'Manage Five local sites':                                  0,
            'Manage Groups':                                            0,
            'Manage Site':                                              0,
            'Manage Transient Object Container':                        0,
            'Manage Vocabulary':                                        0,
            'Manage WebDAV Locks':                                      0,
            'Manage ZCatalog Entries':                                  0,
            'Manage ZCatalogIndex Entries':                             0,
            'Manage portal':                                            0,
            'Manage properties':                                        1,
            'Manage repositories':                                      0,
            'Manage users':                                             0,
            'Modify Cookie Crumblers':                                  0,
            'Modify portal content':                                    1,
            'Modify view template':                                     1,
            'Open/Close Database Connections':                          0,
            'Plone Site Setup: Overview':                               1,
            'Portlets: Manage own portlets':                            1,
            'Portlets: Manage portlets':                                1,
            'Portlets: View dashboard':                                 1,
            'Query Vocabulary':                                         0,
            'Request review':                                           1,
            'Review portal content':                                    1,
            'Search ZCatalog':                                          1,
            'Search for principals':                                    0,
            'Set Group Ownership':                                      0,
            'Set own password':                                         1,
            'Set own properties':                                       1,
            'Sharing page: Delegate Contributor role':                  1,
            'Sharing page: Delegate Editor role':                       1,
            'Sharing page: Delegate Reader role':                       1,
            'Sharing page: Delegate Reviewer role':                     1,
            'Sharing page: Delegate roles':                             1,
            'Take ownership':                                           0,
            'Undo changes':                                             1,
            'Use mailhost services':                                    1,
            'Use version control':                                      1,
            'Reply to item':                                            0,
            'View':                                                     1,
            'View Groups':                                              1,
            'View management screens':                                  0,
            'WebDAV Lock items':                                        1,
            'WebDAV Unlock items':                                      1,
            'WebDAV access':                                            1,
            'plone.portlet.collection: Add collection portlet':         1,
            'plone.portlet.static: Add static portlet':                 1,
        }
        try:
            import plone.app.iterate
            plone.app.iterate  # pyflakes
        except ImportError:
            pass
        else:
            expected.update({
                'iterate : Check in content':                           1,
                'iterate : Check out content':                          1
            })

        site = self.portal
        errors = []
        for p, expected_value in sorted(expected.items(), key=lambda x: x[0]):
            enabled = 'Site Administrator' in rolesForPermissionOn(p, site)
            if expected_value and not enabled:
                errors.append('%s: should be enabled' % p)
            elif enabled and not expected_value:
                errors.append('%s: should be disabled' % p)
        if errors:
            self.fail('Unexpected permissions for Site Administrator role:\n' +
                      ''.join(['\t%s\n' % msg for msg in errors])
                      )
