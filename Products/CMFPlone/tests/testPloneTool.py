from Acquisition import Implicit
from plone.app.testing import SITE_OWNER_NAME
from plone.registry.interfaces import IRegistry
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.interfaces import IReorderedEvent
from Products.CMFPlone.interfaces import ISearchSchema
from Products.CMFPlone.tests import PloneTestCase
from zope.component import getGlobalSiteManager
from zope.component import getUtility
from zope.interface import Interface

default_user = PloneTestCase.default_user
portal_name = PloneTestCase.portal_name


class DummyTitle(Implicit):

    def Title(self):
        # Should just return 'portal_catalog'
        tool = getToolByName(self, 'portal_catalog')
        # Use implicit acquisition even, the horror
        tool = self.portal_catalog
        return tool.getId()

    def getId(self):
        return 'foobar'


class TestPloneTool(PloneTestCase.PloneTestCase):

    def afterSetUp(self):
        self.utils = self.portal.plone_utils

    def testvalidateSingleEmailAddress(self):
        # Any RFC 822 email address allowed, but address list must fail
        val = self.utils.validateSingleEmailAddress
        validInputs = (
            'user@example.org',
            'user@host.example.org',
            'm@t.nu',
            'USER@EXAMPLE.ORG',
            'USER@HOST.EXAMPLE.ORG',
            'USER@hoST.Example.Org',
        )
        invalidInputs = (
            'user@example.org, user2@example.org',  # only single address allowed
            'user@example.org,user2@example.org',
            'user@example.org\n\nfoo',  # double new lines
            'user@example.org\n\rfoo',
            'user@example.org\r\nfoo',
            'user@example.org\r\rfoo',
            # only single address allowed, even if given one per line
            'user@example.org\nfoo@example.org',
            'user@example.org\nBcc: user@example.org',
            'user@example.org\nCc: user@example.org',
            'user@example.org\nSubject: Spam',
            # and a full email (note the missing ,!)
            'From: foo@example.org\n'
            'To: bar@example.org, spam@example.org\n'
            'Cc: egg@example.org\n'
            'Subject: Spam me plenty\n'
            'Spam Spam Spam\n'
            'I hate spam',
        )
        for address in validInputs:
            self.assertTrue(val(address), '%s should validate' % address)
        for address in invalidInputs:
            self.assertFalse(val(address), '%s should fail' % address)

    def testvalidateEmailAddresses(self):
        # Any RFC 822 email address allowed and address list allowed
        val = self.utils.validateEmailAddresses

        validInputs = (
            'user@example.org',
            'user@example.org,\n user2@example.org',
            'user@example.org\n user2@example.org',  # omitting comma is ok
            'USER@EXAMPLE.ORG,\n User2@Example.Org',
        )
        invalidInputs = (
            'user@example.org\n\nfoo',  # double new lines
            'user@example.org\n\rfoo',
            'user@example.org\r\nfoo',
            'user@example.org\r\rfoo',
        )
        for address in validInputs:
            self.assertTrue(val(address), '%s should validate' % address)
        for address in invalidInputs:
            self.assertFalse(val(address), '%s should fail' % address)

    def testNormalizeStringPunctuation(self):
        # Punctuation and spacing is removed and replaced by '-'
        self.assertEqual(self.utils.normalizeString("a string with spaces"),
                         'a-string-with-spaces')
        self.assertEqual(self.utils.normalizeString("p.u,n;c(t)u!a@t#i$o%n"),
                         'p-u-n-c-t-u-a-t-i-o-n')

    def testNormalizeStringFileExtensions(self):
        # The plone tool version uses the id normalizer, so it doesn't
        # preservce file extensions. Use the file name normalizer from
        # plone.i18n if you need the behavior.
        self.assertEqual(self.utils.normalizeString("this is a file.gif"),
                         'this-is-a-file-gif')
        self.assertEqual(self.utils.normalizeString("its. also. a file.html"),
                         'its-also-a-file-html')

    def testNormalizeStringIgnoredCharacters(self):
        # Some characters should be ignored
        self.assertEqual(self.utils.normalizeString("test'test"), 'testtest')

    def testNormalizeStringObject(self):
        # Objects should be converted to strings using repr()
        self.assertEqual(self.utils.normalizeString(None), 'none')
        self.assertEqual(self.utils.normalizeString(True), 'true')
        self.assertEqual(self.utils.normalizeString(False), 'false')

    def testNormalizeStringDangerousCharsInExtension(self):
        # Punctuation and spacing is removed and replaced by '-'
        self.assertEqual(self.utils.normalizeString("A String.a#b"),
                         'a-string-a-b')

    def testTypesToList(self):
        # Make sure typesToList() returns the expected types
        wl = self.utils.typesToList()
        self.assertTrue('Folder' in wl)
        self.assertTrue('Document' in wl)
        self.assertFalse('ATReferenceCriterion' in wl)

    def testGetUserFriendlyTypes(self):
        ttool = getToolByName(self.portal, 'portal_types')
        types = set(ttool.keys())
        registry = getUtility(IRegistry)
        search_settings = registry.forInterface(ISearchSchema, prefix="plone")
        blacklistedTypes = search_settings.types_not_searched

        # 'ChangeSet' is blacklisted, but not in the types by default,
        # so we filter that out.
        blacklistedTypes = {t for t in blacklistedTypes if t in types}
        # No black listed types should be returned.
        self.assertEqual([t for t in self.utils.getUserFriendlyTypes()
                          if t in blacklistedTypes], [])
        self.assertEqual(len(self.utils.getUserFriendlyTypes()),
                         len(types) - len(blacklistedTypes))
        # Non-existing types should be filtered out.
        self.assertEqual(self.utils.getUserFriendlyTypes(
            ['File']), ['File'])
        self.assertEqual(self.utils.getUserFriendlyTypes(
            ['File', 'Non Existing Type']), ['File'])

    def testReindexOnReorder(self):
        gsm = getGlobalSiteManager()
        reordered_parents = []

        def my_handler(obj, event):
            reordered_parents.append(obj)
        gsm.registerHandler(my_handler, (Interface, IReorderedEvent))

        try:
            self.utils.reindexOnReorder("fake_context")
        finally:
            gsm.unregisterHandler(my_handler, (Interface, IReorderedEvent))
        self.assertEqual(["fake_context"], reordered_parents)


class TestOwnershipStuff(PloneTestCase.PloneTestCase):

    def afterSetUp(self):
        self.utils = self.portal.plone_utils
        self.membership = self.portal.portal_membership
        self.membership.addMember('new_owner', 'secret', ['Member'], [])
        self.folder.invokeFactory('Folder', 'folder1')
        self.folder1 = self.folder.folder1
        self.folder1.invokeFactory('Folder', 'folder2')
        self.folder2 = self.folder1.folder2
        self.folder2.invokeFactory('Folder', 'folder3')
        self.folder3 = self.folder2.folder3

    def assertList(self, result, expect):
        # Verifies lists have the same contents
        lhs = [r for r in result]
        lhs.sort()
        rhs = list(expect)
        rhs.sort()
        self.assertEqual(lhs, rhs)

    def testChangeOwnershipOf(self):
        # Should take ownership
        self.assertEqual(self.folder1.getOwnerTuple()[1], default_user)
        self.assertList(self.folder1.get_local_roles_for_userid(default_user),
                        ['Owner'])

        self.utils.changeOwnershipOf(self.folder1, 'new_owner')
        self.assertEqual(self.folder1.getOwnerTuple()[0], [portal_name,
                                                           'acl_users'])
        self.assertEqual(self.folder1.getOwnerTuple()[1], 'new_owner')
        self.assertList(self.folder1.get_local_roles_for_userid('new_owner'),
                        ['Owner'])

        # Initial creator no longer has Owner role.
        self.assertList(
            self.folder1.get_local_roles_for_userid(default_user), [])

    def testChangeOwnershipOfWithTopAclUsers(self):
        # Should be able to give ownership to a user in the top level
        # acl_users folder (even if this is not offered TTW).
        self.utils.changeOwnershipOf(self.folder1, SITE_OWNER_NAME)
        self.assertEqual(self.folder1.getOwnerTuple()[0], ['acl_users'])
        self.assertEqual(self.folder1.getOwnerTuple()[1], SITE_OWNER_NAME)
        self.assertList(
            self.folder1.get_local_roles_for_userid(SITE_OWNER_NAME),
            ['Owner'])

        # Initial creator no longer has Owner role.
        self.assertList(
            self.folder1.get_local_roles_for_userid(default_user), [])

    def testChangeOwnershipOfKeepsOtherRoles(self):
        # Should preserve roles other than Owner
        self.folder1.manage_addLocalRoles('new_owner', ('Reviewer',))
        self.assertList(self.folder1.get_local_roles_for_userid('new_owner'),
                        ['Reviewer'])
        self.utils.changeOwnershipOf(self.folder1, 'new_owner')
        self.assertEqual(self.folder1.getOwnerTuple()[1], 'new_owner')
        self.assertList(self.folder1.get_local_roles_for_userid('new_owner'),
                        ['Owner', 'Reviewer'])
        self.assertList(
            self.folder1.get_local_roles_for_userid(default_user), [])

    def testChangeOwnershipOfRecursive(self):
        # Should take ownership of subobjects as well
        self.utils.changeOwnershipOf(self.folder1, 'new_owner', recursive=1)
        self.assertEqual(self.folder1.getOwnerTuple()[1], 'new_owner')
        self.assertList(self.folder1.get_local_roles_for_userid('new_owner'),
                        ['Owner'])
        self.assertList(
            self.folder1.get_local_roles_for_userid(default_user), [])
        self.assertEqual(self.folder2.getOwnerTuple()[1], 'new_owner')
        self.assertList(self.folder2.get_local_roles_for_userid('new_owner'),
                        ['Owner'])
        self.assertList(
            self.folder2.get_local_roles_for_userid(default_user), [])
        self.assertEqual(self.folder3.getOwnerTuple()[1], 'new_owner')
        self.assertList(self.folder3.get_local_roles_for_userid('new_owner'),
                        ['Owner'])
        self.assertList(
            self.folder3.get_local_roles_for_userid(default_user), [])

    def testGetOwnerName(self):
        # Test that getOwnerName gets the Owner name
        self.assertEqual(self.utils.getOwnerName(self.folder1), default_user)
        self.utils.changeOwnershipOf(self.folder1, 'new_owner')
        self.assertEqual(self.utils.getOwnerName(self.folder1), 'new_owner')

    def testGetInheritedLocalRoles(self):
        # Test basic local roles acquisition is dealt with by
        # getInheritedLocalRoles
        gILR = self.utils.getInheritedLocalRoles
        self.folder1.manage_addLocalRoles('new_owner', ('Reviewer',))
        # Test Normal role acquisition is returned
        filtered_roles = [r for r in gILR(self.folder2)
                          if r[0] == 'new_owner'][0]
        self.assertList(filtered_roles[1], ['Reviewer'])
        filtered_roles = [r for r in gILR(self.folder3)
                          if r[0] == 'new_owner'][0]
        self.assertList(filtered_roles[1], ['Reviewer'])

    def testGetInheritedLocalRolesMultiLevel(self):
        # Test for http://dev.plone.org/plone/ticket/3901
        # make sure local roles are picked up from all folders in tree.
        gILR = self.utils.getInheritedLocalRoles
        self.folder1.manage_addLocalRoles('new_owner', ('Reviewer',))
        self.folder2.manage_addLocalRoles('new_owner', ('Owner',))

        # folder2 should have only the inherited role
        filtered_roles = [r for r in gILR(self.folder2)
                          if r[0] == 'new_owner'][0]
        self.assertList(filtered_roles[1], ['Reviewer'])

        # folder3 should have roles inherited from parent and grand-parent
        filtered_roles = [r for r in gILR(self.folder3)
                          if r[0] == 'new_owner'][0]
        self.assertList(filtered_roles[1], ['Owner', 'Reviewer'])


class TestEditMetadata(PloneTestCase.PloneTestCase):

    def afterSetUp(self):
        self.utils = self.portal.plone_utils
        self.folder.invokeFactory('Document', id='doc')
        self.doc = self.folder.doc

    def testSetTitle(self):
        self.assertEqual(self.doc.Title(), '')
        self.utils.editMetadata(self.doc, title='Foo')
        self.assertEqual(self.doc.Title(), 'Foo')

    def testClearTitle(self):
        self.utils.editMetadata(self.doc, title='Foo')
        self.assertEqual(self.doc.Title(), 'Foo')
        self.utils.editMetadata(self.doc, title='')
        self.assertEqual(self.doc.Title(), '')

    def testSetDescription(self):
        self.assertEqual(self.doc.Description(), '')
        self.utils.editMetadata(self.doc, description='Foo')
        self.assertEqual(self.doc.Description(), 'Foo')

    def testClearDescription(self):
        self.utils.editMetadata(self.doc, description='Foo')
        self.assertEqual(self.doc.Description(), 'Foo')
        self.utils.editMetadata(self.doc, description='')
        self.assertEqual(self.doc.Description(), '')

    def testSetSubject(self):
        self.assertEqual(self.doc.Subject(), ())
        self.utils.editMetadata(self.doc, subject=['Foo'])
        self.assertEqual(self.doc.Subject(), ('Foo',))

    def testClearSubject(self):
        self.utils.editMetadata(self.doc, subject=['Foo'])
        self.assertEqual(self.doc.Subject(), ('Foo',))
        self.utils.editMetadata(self.doc, subject=[])
        self.assertEqual(self.doc.Subject(), ())

    def testSetContributors(self):
        self.assertEqual(self.doc.Contributors(), ())
        self.utils.editMetadata(self.doc, contributors=['Foo'])
        self.assertEqual(self.doc.Contributors(), ('Foo',))

    def testClearContributors(self):
        self.utils.editMetadata(self.doc, contributors=['Foo'])
        self.assertEqual(self.doc.Contributors(), ('Foo',))
        self.utils.editMetadata(self.doc, contributors=[])
        self.assertEqual(self.doc.Contributors(), ())

    def testSetFormat(self):
        self.assertEqual(self.doc.Format(), 'text/html')
        self.assertEqual(self.doc.format, 'text/html')
        self.utils.editMetadata(self.doc, format='text/x-rst')
        self.assertEqual(self.doc.format, 'text/x-rst')
        self.assertEqual(self.doc.Format(), 'text/x-rst')

    def testClearFormat(self):
        self.utils.editMetadata(self.doc, format='text/x-rst')
        self.assertEqual(self.doc.format, 'text/x-rst')
        self.assertEqual(self.doc.Format(), 'text/x-rst')
        self.utils.editMetadata(self.doc, format='')
        self.assertEqual(self.doc.Format(), '')
        self.assertEqual(self.doc.format, '')

    def testSetLanguage(self):
        self.assertEqual(self.doc.Language(), '')
        self.utils.editMetadata(self.doc, language='de')
        self.assertEqual(self.doc.Language(), 'de')

    def testClearLanguage(self):
        self.utils.editMetadata(self.doc, language='de')
        self.assertEqual(self.doc.Language(), 'de')
        self.utils.editMetadata(self.doc, language='')
        self.assertEqual(self.doc.Language(), '')

    def testSetRights(self):
        self.assertEqual(self.doc.Rights(), '')
        self.utils.editMetadata(self.doc, rights='Foo')
        self.assertEqual(self.doc.Rights(), 'Foo')

    def testClearRights(self):
        self.utils.editMetadata(self.doc, rights='Foo')
        self.assertEqual(self.doc.Rights(), 'Foo')
        self.utils.editMetadata(self.doc, rights='')
        self.assertEqual(self.doc.Rights(), '')

    # Also test the various dates

    def testSetEffectiveDate(self):
        self.assertEqual(self.doc.EffectiveDate(), 'None')
        self.utils.editMetadata(self.doc, effective_date='2001-01-01')
        self.assertTrue(self.doc.effective_date.ISO8601()
                            .startswith('2001-01-01T00:00:00'))

    def testClearEffectiveDate(self):
        self.utils.editMetadata(self.doc, effective_date='2001-01-01')
        self.assertTrue(self.doc.effective_date.ISO8601()
                            .startswith('2001-01-01T00:00:00'))
        self.utils.editMetadata(self.doc, effective_date='None')
        self.assertEqual(self.doc.EffectiveDate(), 'None')
        self.assertEqual(self.doc.effective_date, None)

    def testSetExpirationDate(self):
        self.assertEqual(self.doc.ExpirationDate(), 'None')
        self.utils.editMetadata(self.doc, expiration_date='2001-01-01')
        self.assertTrue(self.doc.expiration_date.ISO8601()
                            .startswith('2001-01-01T00:00:00'))

    def testClearExpirationDate(self):
        self.utils.editMetadata(self.doc, expiration_date='2001-01-01')
        self.assertTrue(self.doc.expiration_date.ISO8601()
                            .startswith('2001-01-01T00:00:00'))
        self.utils.editMetadata(self.doc, expiration_date='None')
        self.assertEqual(self.doc.ExpirationDate(), 'None')
        self.assertEqual(self.doc.expiration_date, None)

    # Test special cases of tuplification

    def testTuplifySubject_1(self):
        self.utils.editMetadata(self.doc, subject=['Foo', 'Bar', 'Baz'])
        self.assertEqual(self.doc.Subject(), ('Foo', 'Bar', 'Baz'))

    def testTuplifySubject_2(self):
        self.utils.editMetadata(self.doc, subject=['Foo', '', 'Bar', 'Baz'])
        # Note that empty entries are filtered
        self.assertEqual(self.doc.Subject(), ('Foo', 'Bar', 'Baz'))

    def DISABLED_testTuplifySubject_3(self):
        self.utils.editMetadata(self.doc, subject='Foo, Bar, Baz')
        # TODO: Wishful thinking
        self.assertEqual(self.doc.Subject(), ('Foo', 'Bar', 'Baz'))

    def testTuplifyContributors_1(self):
        self.utils.editMetadata(self.doc, contributors=['Foo', 'Bar', 'Baz'])
        self.assertEqual(self.doc.Contributors(), ('Foo', 'Bar', 'Baz'))

    def testTuplifyContributors_2(self):
        self.utils.editMetadata(self.doc,
                                contributors=['Foo', '', 'Bar', 'Baz'])
        # Note that empty entries are filtered
        self.assertEqual(self.doc.Contributors(), ('Foo', 'Bar', 'Baz'))

    def DISABLED_testTuplifyContributors_3(self):
        self.utils.editMetadata(self.doc, contributors='Foo; Bar; Baz')
        # TODO: Wishful thinking
        self.assertEqual(self.doc.Contributors(), ('Foo', 'Bar', 'Baz'))


class TestEditMetadataIndependence(PloneTestCase.PloneTestCase):

    def afterSetUp(self):
        self.utils = self.portal.plone_utils
        self.folder.invokeFactory('Document', id='doc')
        self.doc = self.folder.doc
        self.utils.editMetadata(self.doc,
                                title='Foo',
                                subject=('Bar',),
                                description='Baz',
                                contributors=('Fred',),
                                effective_date='2001-01-01',
                                expiration_date='2003-01-01',
                                format='text/html',
                                language='de',
                                rights='Copyleft',
                                )

    def testEditTitleOnly(self):
        self.utils.editMetadata(self.doc, title='Oh Happy Day')
        self.assertEqual(self.doc.Title(), 'Oh Happy Day')
        # Other elements must not change
        self.assertEqual(self.doc.Subject(), ('Bar',))
        self.assertEqual(self.doc.Description(), 'Baz')
        self.assertEqual(self.doc.Contributors(), ('Fred',))
        self.assertTrue(self.doc.effective_date.ISO8601()
                            .startswith('2001-01-01T00:00:00'))
        self.assertTrue(self.doc.expiration_date.ISO8601()
                            .startswith('2003-01-01T00:00:00'))
        self.assertEqual(self.doc.Format(), 'text/html')
        self.assertEqual(self.doc.Language(), 'de')
        self.assertEqual(self.doc.Rights(), 'Copyleft')

    def testEditSubjectOnly(self):
        self.utils.editMetadata(self.doc, subject=('Oh', 'Happy', 'Day'))
        self.assertEqual(self.doc.Subject(), ('Oh', 'Happy', 'Day'))
        # Other elements must not change
        self.assertEqual(self.doc.Title(), 'Foo')
        self.assertEqual(self.doc.Description(), 'Baz')
        self.assertEqual(self.doc.Contributors(), ('Fred',))
        self.assertTrue(self.doc.effective_date.ISO8601()
                            .startswith('2001-01-01T00:00:00'))
        self.assertTrue(self.doc.expiration_date.ISO8601()
                            .startswith('2003-01-01T00:00:00'))
        self.assertEqual(self.doc.Format(), 'text/html')
        self.assertEqual(self.doc.Language(), 'de')
        self.assertEqual(self.doc.Rights(), 'Copyleft')

    def testEditEffectiveDateOnly(self):
        self.utils.editMetadata(self.doc, effective_date='2001-12-31')
        self.assertTrue(self.doc.effective_date.ISO8601()
                            .startswith('2001-12-31T00:00:00'))
        # Other elements must not change
        self.assertEqual(self.doc.Title(), 'Foo')
        self.assertEqual(self.doc.Subject(), ('Bar',))
        self.assertEqual(self.doc.Description(), 'Baz')
        self.assertEqual(self.doc.Contributors(), ('Fred',))
        self.assertTrue(self.doc.expiration_date.ISO8601()
                            .startswith('2003-01-01T00:00:00'))
        self.assertEqual(self.doc.Format(), 'text/html')
        self.assertEqual(self.doc.Language(), 'de')
        self.assertEqual(self.doc.Rights(), 'Copyleft')

    def testEditLanguageOnly(self):
        self.utils.editMetadata(self.doc, language='fr')
        self.assertEqual(self.doc.Language(), 'fr')
        # Other elements must not change
        self.assertEqual(self.doc.Title(), 'Foo')
        self.assertEqual(self.doc.Subject(), ('Bar',))
        self.assertEqual(self.doc.Description(), 'Baz')
        self.assertEqual(self.doc.Contributors(), ('Fred',))
        self.assertTrue(self.doc.effective_date.ISO8601()
                            .startswith('2001-01-01T00:00:00'))
        self.assertTrue(self.doc.expiration_date.ISO8601()
                            .startswith('2003-01-01T00:00:00'))
        self.assertEqual(self.doc.Format(), 'text/html')
        self.assertEqual(self.doc.Rights(), 'Copyleft')


class TestBreadCrumbs(PloneTestCase.PloneTestCase):
    '''Tests for the portal tabs query'''

    def afterSetUp(self):
        self.utils = self.portal.plone_utils
        self.populateSite()

    def populateSite(self):
        self.setRoles(['Manager'])
        self.portal.invokeFactory('Folder', 'folder1')
        folder1 = getattr(self.portal, 'folder1')
        folder1.invokeFactory('Document', 'doc11')
        folder1.invokeFactory('File', 'file11')
        self.setRoles(['Member'])

    def testCreateBreadCrumbs(self):
        # See if we can create one at all
        doc = self.portal.folder1.doc11
        crumbs = self.utils.createBreadCrumbs(doc)
        self.assertTrue(crumbs)
        self.assertEqual(len(crumbs), 2)
        self.assertEqual(crumbs[-1]['absolute_url'], doc.absolute_url())
        self.assertEqual(crumbs[-2]['absolute_url'],
                         doc.aq_parent.absolute_url())

    def testBreadcrumbsRespectTypesWithViewAction(self):
        # With a type in types_use_view_action_in_listings as current action it
        # should return a breadcrumb which has '/view' appended to the url
        file = self.portal.folder1.file11
        crumbs = self.utils.createBreadCrumbs(file)
        self.assertTrue(crumbs)
        self.assertEqual(crumbs[-1]['absolute_url'][-5:], '/view')


class TestIDGenerationMethods(PloneTestCase.PloneTestCase):
    """Tests the isIDAutoGenerated method and pretty_title_or_id
    """

    def afterSetUp(self):
        self.utils = self.portal.plone_utils

    def testAutoGeneratedId(self):
        r = self.utils.isIDAutoGenerated('document.2004-11-09.0123456789')
        self.assertEqual(r, True)

    def testValidPortalTypeNameButNotAutoGeneratedId(self):
        # This was raising an IndexError exception for
        # Zope < 2.7.3 (DateTime.py < 1.85.12.11) and a
        # SyntaxError for Zope >= 2.7.3 (DateTime.py >= 1.85.12.11)
        r = self.utils.isIDAutoGenerated('document.tar.gz')
        self.assertEqual(r, False)
        r = self.utils.isIDAutoGenerated('document.tar.12/32/2004')
        self.assertEqual(r, False)
        r = self.utils.isIDAutoGenerated('document.tar.12/31/2004 12:62')
        self.assertEqual(r, False)

    def test_pretty_title_or_id_returns_title(self):
        self.folder.setTitle('My pretty title')
        self.assertEqual(self.utils.pretty_title_or_id(self.folder),
                         'My pretty title')

    def test_pretty_title_or_id_returns_id(self):
        self.folder.setTitle('')
        self.assertEqual(self.utils.pretty_title_or_id(self.folder),
                         self.folder.getId())

    def test_pretty_title_or_id_when_autogenerated(self):
        self.setRoles(['Manager', 'Member'])
        self.folder.setTitle('')
        self.folder.__parent__.manage_renameObject(
            self.folder.id, 'folder.2004-11-09.0123456789')
        self.folder.reindexObject()
        self.assertEqual(self.utils.pretty_title_or_id(self.folder),
                         self.utils.getEmptyTitle())
        self.assertEqual(self.utils.pretty_title_or_id(self.folder, 'Marker'),
                         'Marker')

    def test_pretty_title_or_id_works_with_method_that_needs_context(self):
        self.setRoles(['Manager', 'Member'])
        # Create a dummy class that looks at it's context to find the title
        new_obj = DummyTitle()
        new_obj = new_obj.__of__(self.folder)
        try:
            title = self.utils.pretty_title_or_id(new_obj)
        except AttributeError as e:
            self.fail('pretty_title_or_id failed to include context %s' % e)
        self.assertEqual(title, 'portal_catalog')

    def test_pretty_title_or_id_on_catalog_brain(self):
        cat = self.portal.portal_catalog
        self.setRoles(['Manager', 'Member'])
        self.folder.title = 'My pretty title'
        self.folder.subject = ('foobar',)
        self.folder.reindexObject()
        results = cat(Subject='foobar')
        self.assertEqual(len(results), 1)
        self.assertEqual(self.utils.pretty_title_or_id(results[0]),
                         'My pretty title')

    def test_pretty_title_or_id_on_catalog_brain_returns_id(self):
        cat = self.portal.portal_catalog
        self.setRoles(['Manager', 'Member'])
        self.folder.title = ''
        self.folder.subject = ('foobar',)
        self.folder.reindexObject()
        results = cat(Subject='foobar')
        self.assertEqual(len(results), 1)
        self.assertEqual(self.utils.pretty_title_or_id(results[0]),
                         self.folder.getId())

    def test_pretty_title_or_id_on_catalog_brain_autogenerated(self):
        cat = self.portal.portal_catalog
        self.setRoles(['Manager', 'Member'])
        self.folder.__parent__.manage_renameObject(
            self.folder.id, 'folder.2004-11-09.0123456789')
        self.folder.title = ''
        self.folder.subject = ('foobar',)
        self.folder.reindexObject()
        results = cat(Subject='foobar')
        self.assertEqual(len(results), 1)
        self.assertEqual(self.utils.pretty_title_or_id(results[0], 'Marker'),
                         'Marker')

    def test_pretty_title_or_id_on_catalog_brain_no_title(self):
        cat = self.portal.portal_catalog
        self.setRoles(['Manager', 'Member'])
        # Remove Title from catalog metadata to simulate a catalog with no
        # Title metadata and similar pathological cases.
        cat.delColumn('Title')
        self.folder.title = ''
        self.folder.subject = ('foobar',)
        self.folder.reindexObject()
        results = cat(Subject='foobar')
        self.assertEqual(len(results), 1)
        # Give the portal a title because this is what will show up on
        # failure
        self.portal.title = 'This is not the title you are looking for'
        self.assertEqual(self.utils.pretty_title_or_id(results[0]),
                         self.folder.getId())

    def testGetMethodAliases(self):
        fti = self.folder.getTypeInfo()
        expectedAliases = fti.getMethodAliases()
        aliases = self.utils.getMethodAliases(fti)
        self.assertEqual(len(expectedAliases), len(aliases))
        for k, v in aliases.items():
            self.assertEqual(expectedAliases[k], v)
