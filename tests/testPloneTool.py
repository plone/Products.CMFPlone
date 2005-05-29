#
# Tests the PloneTool
#

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase
from Products.CMFPlone.tests import PloneTestCase
from Products.CMFPlone.tests import dummy
from DateTime import DateTime
from Products.CMFPlone.utils import _createObjectByType

default_user = PloneTestCase.default_user


class TestPloneTool(PloneTestCase.PloneTestCase):

    def afterSetUp(self):
        self.utils = self.portal.plone_utils

    def testvalidateSingleEmailAddress(self):
        # Any RFC 822 email address allowed, but address list must fail
        val = self.utils.validateSingleEmailAddress
        validInputs = (
            #'user',
            #'user@foo',
            'user@example.org',
            'user@host.example.org',
            'm@t.nu',
            'USER@EXAMPLE.ORG',
            'USER@HOST.EXAMPLE.ORG',
            'USER@hoST.Example.Org',

            ## Some trickier ones, from RFC 822
            #'"A Name" user @ example',
            #'"A Name" user\n @ example',
            #'nn@[1.2.3.4]'
        )
        invalidInputs = (
            'user@example.org, user2@example.org',   # only single address allowed
            'user@example.org,user2@example.org',
            #'user@example.org;user2@example.org',
            'user@example.org\n\nfoo', # double new lines
            'user@example.org\n\rfoo',
            'user@example.org\r\nfoo',
            'user@example.org\r\rfoo',
            'user@example.org\nfoo@example.org', # only single address allowed, even if given one per line
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
            self.failUnless(val(address), '%s should validate' % address)
        for address in invalidInputs:
            self.failIf(val(address), '%s should fail' % address)
    
    def testvalidateEmailAddresses(self):
        # Any RFC 822 email address allowed and address list allowed
        val = self.utils.validateEmailAddresses

        validInputs = (
            # 'user',
            # 'user@example',
            'user@example.org',
            #'user@example.org\n user2',
            #'user@example.org\r user2',
            'user@example.org,\n user2@example.org',
            'user@example.org\n user2@example.org', # omitting comma is ok
            'USER@EXAMPLE.ORG,\n User2@Example.Org',
        )
        invalidInputs = (
            'user@example.org\n\nfoo', # double new lines
            'user@example.org\n\rfoo',
            'user@example.org\r\nfoo',
            'user@example.org\r\rfoo',
            #py stdlib bug? 'user@example.org\nuser2@example.org', # continuation line doesn't begin with white space
        )
        for address in validInputs:
            self.failUnless(val(address), '%s should validate' % address)
        for address in invalidInputs:
            self.failIf(val(address), '%s should fail' % address)

    def testEditFormatMetadataOfFile(self):
        # Test fix for http://plone.org/collector/1323
        # Fixed in CMFDefault.File, not Plone.
        self.folder.invokeFactory('File', id='file')
        self.folder.file.edit(file=dummy.File('foo.zip'))
        self.assertEqual(self.folder.file.Format(), 'application/zip')
        self.assertEqual(self.folder.file.getFile().content_type, 'application/zip')
        # Changing the format should be reflected in content_type property
        self.utils.editMetadata(self.folder.file, format='image/gif')
        self.assertEqual(self.folder.file.Format(), 'image/gif')
        self.assertEqual(self.folder.file.getFile().content_type, 'image/gif')

    def testEditFormatMetadataOfImage(self):
        # Test fix for http://plone.org/collector/1323
        # Fixed in CMFDefault.Image, not Plone.
        self.folder.invokeFactory('Image', id='image')
        self.folder.image.edit(file=dummy.Image('foo.zip'))
        self.assertEqual(self.folder.image.Format(), 'application/zip')
        self.assertEqual(self.folder.image.getImage().content_type, 'application/zip')
        # Changing the format should be reflected in content_type property
        self.utils.editMetadata(self.folder.image, format='image/gif')
        self.assertEqual(self.folder.image.Format(), 'image/gif')
        self.assertEqual(self.folder.image.getImage().content_type, 'image/gif')

    def testNormalizeStringPunctuation(self):
        # Punctuation and spacing is removed and replaced by '-'
        self.assertEqual(self.utils.normalizeString("a string with spaces"),
                         'a-string-with-spaces')
        self.assertEqual(self.utils.normalizeString("p.u,n;c(t)u!a@t#i$o%n"),
                         'p-u-n-c-t-u-a-t-i-o-n')

    def testNormalizeStringLower(self):
        # Strings are lowercased
        self.assertEqual(self.utils.normalizeString("UppERcaSE"), 'uppercase')

    def testNormalizeStringStrip(self):
        # Punctuation and spaces are trimmed, multiples reduced to 1
        self.assertEqual(self.utils.normalizeString(" a string    "),
                         'a-string')
        self.assertEqual(self.utils.normalizeString(">here's another!"),
                         'here-s-another')
        self.assertEqual(self.utils.normalizeString("one with !@#$!@#$ stuff in the middle"),
                         'one-with-stuff-in-the-middle')

    def testNormalizeStringFileExtensions(self):
        # If there is something that looks like a file extensions
        # it will be preserved.
        self.assertEqual(self.utils.normalizeString("this is a file.gif"),
                         'this-is-a-file.gif')
        self.assertEqual(self.utils.normalizeString("this is. also. a file.html"),
                         'this-is-also-a-file.html')

    def testNormalizeStringAccents(self):
        # European accented chars will be transliterated to rough ASCII equivalents
        input = u"Eksempel \xe6\xf8\xe5 norsk \xc6\xd8\xc5"
        self.assertEqual(self.utils.normalizeString(input),
                         'eksempel-eoa-norsk-eoa')

    def testNormalizeStringUTF8(self):
        # In real life, input will not be Unicode...
        input = u"Eksempel \xe6\xf8\xe5 norsk \xc6\xd8\xc5".encode('utf-8')
        self.assertEqual(self.utils.normalizeString(input),
                         'eksempel-eoa-norsk-eoa')

    def testNormalizeGreek(self):
        # Greek letters (not supported by UnicodeData)
        input = u'\u039d\u03af\u03ba\u03bf\u03c2 \u03a4\u03b6\u03ac\u03bd\u03bf\u03c2'
        self.assertEqual(self.utils.normalizeString(input), 'nikos-tzanos')
 
    def testNormalizeGreekUTF8(self):
        # Greek letters (not supported by UnicodeData)
        input = u'\u039d\u03af\u03ba\u03bf\u03c2 \u03a4\u03b6\u03ac\u03bd\u03bf\u03c2'.encode('utf-8')
        self.assertEqual(self.utils.normalizeString(input), 'nikos-tzanos')
 
    def testNormalizeStringHex(self):
        # Everything that can't be transliterated will be hex'd
        self.assertEqual(self.utils.normalizeString(u"\u9ad8\u8054\u5408 Chinese"),
                         '9ad880545408-chinese')
        self.assertEqual(self.utils.normalizeString(u"\uc774\ubbf8\uc9f1 Korean"),
                         'c774bbf8c9f1-korean')


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
        
        self.folder2.invokeFactory('Document', 'doc1')
        self.doc1 = self.folder2.doc1
        
        # Be able to test old-style folders and docs, too
        _createObjectByType('CMF Folder', self.folder2, 'cmffolder')
        self.cmffolder = self.folder2.cmffolder
        _createObjectByType('CMF Document', self.folder2, 'cmfdoc')
        self.cmfdoc = self.folder2.cmfdoc

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
        self.assertList(self.folder1.get_local_roles_for_userid(default_user), ['Owner'])

        self.utils.changeOwnershipOf(self.folder1, 'new_owner')
        self.assertEqual(self.folder1.getOwnerTuple()[1], 'new_owner')
        self.assertList(self.folder1.get_local_roles_for_userid('new_owner'), ['Owner'])

        # Initial creator no longer has Owner role.
        self.assertList(self.folder1.get_local_roles_for_userid(default_user), [])

    def testChangeOwnershipOfKeepsOtherRoles(self):
        # Should preserve roles other than Owner
        self.folder1.manage_addLocalRoles('new_owner', ('Reviewer',))
        self.assertList(self.folder1.get_local_roles_for_userid('new_owner'), ['Reviewer'])
        self.utils.changeOwnershipOf(self.folder1, 'new_owner')
        self.assertEqual(self.folder1.getOwnerTuple()[1], 'new_owner')
        self.assertList(self.folder1.get_local_roles_for_userid('new_owner'), ['Owner', 'Reviewer'])
        self.assertList(self.folder1.get_local_roles_for_userid(default_user), [])

    def testChangeOwnershipOfRecursive(self):
        # Should take ownership of subobjects as well
        self.utils.changeOwnershipOf(self.folder1, 'new_owner', recursive=1)
        self.assertEqual(self.folder1.getOwnerTuple()[1], 'new_owner')
        self.assertList(self.folder1.get_local_roles_for_userid('new_owner'), ['Owner'])
        self.assertList(self.folder1.get_local_roles_for_userid(default_user), [])
        self.assertEqual(self.folder2.getOwnerTuple()[1], 'new_owner')
        self.assertList(self.folder2.get_local_roles_for_userid('new_owner'), ['Owner'])
        self.assertList(self.folder2.get_local_roles_for_userid(default_user), [])
        self.assertEqual(self.folder3.getOwnerTuple()[1], 'new_owner')
        self.assertList(self.folder3.get_local_roles_for_userid('new_owner'), ['Owner'])
        self.assertList(self.folder3.get_local_roles_for_userid(default_user), [])

    def testChangeOwnershipOfFolderChangesCreator(self):
        # Test both AT and CMF folders
        self.utils.changeOwnershipOf(self.folder1, 'new_owner')
        self.utils.changeOwnershipOf(self.cmffolder, 'new_owner')
        self.assertEqual(self.folder1.Creator(), 'new_owner')
        self.assertEqual(self.cmffolder.Creator(), 'new_owner')
        
    def testChangeOwnershipOfDocumentChangesCreator(self):
       # Test both AT and CMF documents
        self.utils.changeOwnershipOf(self.doc1, 'new_owner')
        self.utils.changeOwnershipOf(self.cmfdoc, 'new_owner')
        self.assertEqual(self.doc1.Creator(), 'new_owner')
        self.assertEqual(self.cmfdoc.Creator(), 'new_owner')

    def testChangeOwnershipOfChangesCreatorRecursive(self):
        self.utils.changeOwnershipOf(self.folder1, 'new_owner', recursive=1)
        self.assertEquals(self.folder1.Creator(), 'new_owner')
        self.assertEquals(self.folder2.Creator(), 'new_owner')
        self.assertEquals(self.folder3.Creator(), 'new_owner')
        self.assertEquals(self.cmffolder.Creator(), 'new_owner')
        self.assertEquals(self.doc1.Creator(), 'new_owner')
        self.assertEquals(self.cmfdoc.Creator(), 'new_owner')
        
    def testGetOwnerId(self):
        # Test that getOwnerId gets the Owner Id
        self.assertEqual(self.utils.getOwnerId(self.folder1), default_user)
        self.utils.changeOwnershipOf(self.folder1, 'new_owner')
        self.assertEqual(self.utils.getOwnerId(self.folder1), 'new_owner')

    def testGetInheritedLocalRoles(self):
        # Test basic local roles acquisition is dealt with by
        # getInheritedLocalRoles
        gILR = self.utils.getInheritedLocalRoles
        self.folder1.manage_addLocalRoles('new_owner', ('Reviewer',))
        # Test Normal role acquisition is returned
        filtered_roles = [r for r in gILR(self.folder2) if r[0] == 'new_owner'][0]
        self.assertList(filtered_roles[1], ['Reviewer'])
        filtered_roles = [r for r in gILR(self.folder3) if r[0] == 'new_owner'][0]
        self.assertList(filtered_roles[1], ['Reviewer'])

    def testGetInheritedLocalRolesMultiLevel(self):
        # Test for http://members.plone.org/collector/3901
        # make sure local roles are picked up from all folders in tree.
        gILR = self.utils.getInheritedLocalRoles
        self.folder1.manage_addLocalRoles('new_owner', ('Reviewer',))
        self.folder2.manage_addLocalRoles('new_owner', ('Owner',))

        # folder2 should have only the inherited role
        filtered_roles = [r for r in gILR(self.folder2) if r[0] == 'new_owner'][0]
        self.assertList(filtered_roles[1], ['Reviewer'])

        # folder3 should have roles inherited from parent and grand-parent
        filtered_roles = [r for r in gILR(self.folder3) if r[0] == 'new_owner'][0]
        self.assertList(filtered_roles[1], ['Owner','Reviewer'])


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
        self.assertEqual(self.doc.text_format, 'text/html')
        self.utils.editMetadata(self.doc, format='text/x-rst')
        self.assertEqual(self.doc.Format(), 'text/x-rst')
        self.assertEqual(self.doc.text_format, 'text/x-rst')

    def testClearFormat(self):
        self.utils.editMetadata(self.doc, format='text/x-rst')
        self.assertEqual(self.doc.Format(), 'text/x-rst')
        self.assertEqual(self.doc.text_format, 'text/x-rst')
        self.utils.editMetadata(self.doc, format='')
        self.assertEqual(self.doc.Format(), 'text/html')
        self.assertEqual(self.doc.text_format, 'text/html')

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
        self.assertEqual(self.doc.EffectiveDate(), '2001-01-01 00:00:00')

    def testClearEffectiveDate(self):
        self.utils.editMetadata(self.doc, effective_date='2001-01-01')
        self.assertEqual(self.doc.EffectiveDate(), '2001-01-01 00:00:00')
        self.utils.editMetadata(self.doc, effective_date='None')
        self.assertEqual(self.doc.EffectiveDate(), 'None')
        self.assertEqual(self.doc.effective_date, None)

    def testSetExpirationDate(self):
        self.assertEqual(self.doc.ExpirationDate(), 'None')
        self.utils.editMetadata(self.doc, expiration_date='2001-01-01')
        self.assertEqual(self.doc.ExpirationDate(), '2001-01-01 00:00:00')

    def testClearExpirationDate(self):
        self.utils.editMetadata(self.doc, expiration_date='2001-01-01')
        self.assertEqual(self.doc.ExpirationDate(), '2001-01-01 00:00:00')
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
        # XXX: Wishful thinking
        self.assertEqual(self.doc.Subject(), ('Foo', 'Bar', 'Baz'))
        
    def testTuplifyContributors_1(self):
        self.utils.editMetadata(self.doc, contributors=['Foo', 'Bar', 'Baz'])
        self.assertEqual(self.doc.Contributors(), ('Foo', 'Bar', 'Baz'))
        
    def testTuplifyContributors_2(self):
        self.utils.editMetadata(self.doc, contributors=['Foo', '', 'Bar', 'Baz'])
        # Note that empty entries are filtered
        self.assertEqual(self.doc.Contributors(), ('Foo', 'Bar', 'Baz'))

    def DISABLED_testTuplifyContributors_3(self):
        self.utils.editMetadata(self.doc, contributors='Foo; Bar; Baz')
        # XXX: Wishful thinking
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
        self.assertEqual(self.doc.EffectiveDate(), '2001-01-01 00:00:00')
        self.assertEqual(self.doc.ExpirationDate(), '2003-01-01 00:00:00')
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
        self.assertEqual(self.doc.EffectiveDate(), '2001-01-01 00:00:00')
        self.assertEqual(self.doc.ExpirationDate(), '2003-01-01 00:00:00')
        self.assertEqual(self.doc.Format(), 'text/html')
        self.assertEqual(self.doc.Language(), 'de')
        self.assertEqual(self.doc.Rights(), 'Copyleft')

    def testEditEffectiveDateOnly(self):
        self.utils.editMetadata(self.doc, effective_date='2001-12-31')
        self.assertEqual(self.doc.EffectiveDate(), '2001-12-31 00:00:00')
        # Other elements must not change
        self.assertEqual(self.doc.Title(), 'Foo')
        self.assertEqual(self.doc.Subject(), ('Bar',))
        self.assertEqual(self.doc.Description(), 'Baz')
        self.assertEqual(self.doc.Contributors(), ('Fred',))
        self.assertEqual(self.doc.ExpirationDate(), '2003-01-01 00:00:00')
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
        self.assertEqual(self.doc.EffectiveDate(), '2001-01-01 00:00:00')
        self.assertEqual(self.doc.ExpirationDate(), '2003-01-01 00:00:00')
        self.assertEqual(self.doc.Format(), 'text/html')
        self.assertEqual(self.doc.Rights(), 'Copyleft')


class TestFormulatorFields(PloneTestCase.PloneTestCase):
    '''This feature should probably go away entirely.'''

    def afterSetUp(self):
        self.utils = self.portal.plone_utils
        self.folder.invokeFactory('Document', id='doc')
        self.doc = self.folder.doc

    def setField(self, name, value):
        form = self.app.REQUEST.form
        pfx = self.utils.field_prefix
        form[pfx+name] = value

    def testTitleField(self):
        self.setField('title', 'Foo')
        self.utils.editMetadata(self.doc)
        self.assertEqual(self.doc.Title(), 'Foo')

    def testSubjectField(self):
        self.setField('subject', ['Foo', 'Bar', 'Baz'])
        self.utils.editMetadata(self.doc)
        self.assertEqual(self.doc.Subject(), ('Foo', 'Bar', 'Baz'))

    def testEffectiveDateField(self):
        self.setField('effective_date', '2001-01-01')
        self.utils.editMetadata(self.doc)
        self.assertEqual(self.doc.EffectiveDate(), '2001-01-01 00:00:00')

    def testLanguageField(self):
        self.setField('language', 'de')
        self.utils.editMetadata(self.doc)
        # XXX: Note that language, format, and rights do not 
        #      receive the Formulator treatment.
        self.assertEqual(self.doc.Language(), '')


class TestNavTree(PloneTestCase.PloneTestCase):
    '''Tests for the new navigation tree and sitemap'''

    def afterSetUp(self):
        self.utils = self.portal.plone_utils
        self.populateSite()

    def populateSite(self):
        self.setRoles(['Manager'])
        self.portal.invokeFactory('Document', 'doc1')
        self.portal.invokeFactory('Document', 'doc2')
        self.portal.invokeFactory('Document', 'doc3')
        self.portal.invokeFactory('Folder', 'folder1')
        folder1 = getattr(self.portal, 'folder1')
        folder1.invokeFactory('Document', 'doc11')
        folder1.invokeFactory('Document', 'doc12')
        folder1.invokeFactory('Document', 'doc13')
        self.portal.invokeFactory('Folder', 'folder2')
        folder2 = getattr(self.portal, 'folder2')
        folder2.invokeFactory('Document', 'doc21')
        folder2.invokeFactory('Document', 'doc22')
        folder2.invokeFactory('Document', 'doc23')
        folder2.invokeFactory('File', 'file21')
        self.setRoles(['Member'])

    def testCreateNavTree(self):
        # See if we can create one at all
        tree = self.utils.createNavTree(self.portal)
        self.failUnless(tree)
        self.failUnless(tree.has_key('children'))

    def testCreateNavTreeCurrentItem(self):
        # With the context set to folder2 it should return a dict with
        # currentItem set to True
        tree = self.utils.createNavTree(self.portal.folder2)
        self.failUnless(tree)
        self.assertEqual(tree['children'][-1]['currentItem'], True)

    def testCreateNavTreeRespectsTypesWithViewAction(self):
        # With a File or Image as current action it should return a
        # currentItem which has '/view' appended to the url
        tree = self.utils.createNavTree(self.portal.folder2.file21)
        self.failUnless(tree)
        # Fail if 'view' is used for parent folder; it should only be on the File
        self.failIf(tree['children'][-1]['absolute_url'][-5:]=='/view')
        # Verify we have the correct object and it is the current item
        self.assertEqual(tree['children'][-1]['children'][-1]['currentItem'],True)
        self.assertEqual(tree['children'][-1]['children'][-1]['path'].split('/')[-1],'file21')
        # Verify that we have '/view'
        self.assertEqual(tree['children'][-1]['children'][-1]['absolute_url'][-5:],'/view')

    def testNavTreeExcludesItemsWithExcludeProperty(self):
        # Make sure that items witht he exclude_from_nav property set get
        # no_display set to True
        self.portal.folder2.manage_addProperty('exclude_from_nav',True,'boolean')
        self.portal.folder2.reindexObject()
        tree = self.utils.createNavTree(self.portal.folder2.file21)
        self.failUnless(tree)
        self.assertEqual(tree['children'][-1]['no_display'],True)
        # Shouldn't exlude anything else
        self.assertEqual(tree['children'][0]['no_display'],False)

    def testNavTreeExcludesItemsInIdsNotToList(self):
        # Make sure that items whose ids are in the idsNotToList navTree
        # property get no_display set to True
        ntp=self.portal.portal_properties.navtree_properties
        ntp.manage_changeProperties(idsNotToList=['folder2'])
        tree = self.utils.createNavTree(self.portal.folder2.file21)
        self.failUnless(tree)
        self.assertEqual(tree['children'][-1]['no_display'],True)
        # Shouldn't exlude anything else
        self.assertEqual(tree['children'][0]['no_display'],False)

    def testCreateSitemap(self):
        # Internally createSitemap is the same as createNavTree
        tree = self.utils.createSitemap(self.portal)
        self.failUnless(tree)

    def testCustomQuery(self):
        # Try a custom query script for the navtree that returns only published
        # objects
        workflow = self.portal.portal_workflow
        factory = self.portal.manage_addProduct['PythonScripts']
        factory.manage_addPythonScript('getCustomNavQuery')
        script = self.portal.getCustomNavQuery
        script.ZPythonScript_edit('','return {"review_state":"published"}')
        self.assertEqual(self.portal.getCustomNavQuery(),{"review_state":"published"})
        tree = self.utils.createNavTree(self.portal.folder2)
        self.failUnless(tree)
        self.failUnless(tree.has_key('children'))
        #Should only contain current object
        self.assertEqual(len(tree['children']), 1)
        #change workflow for folder1
        workflow.doActionFor(self.portal.folder1, 'publish')
        self.portal.folder1.reindexObject()
        tree = self.utils.createNavTree(self.portal.folder2)
        #Should only contain current object and published folder
        self.assertEqual(len(tree['children']), 2)


class TestPortalTabs(PloneTestCase.PloneTestCase):
    '''Tests for the portal tabs query'''

    def afterSetUp(self):
        self.utils = self.portal.plone_utils
        self.populateSite()

    def populateSite(self):
        self.setRoles(['Manager'])
        self.portal.invokeFactory('Document', 'doc1')
        self.portal.invokeFactory('Document', 'doc2')
        self.portal.invokeFactory('Document', 'doc3')
        self.portal.invokeFactory('Folder', 'folder1')
        folder1 = getattr(self.portal, 'folder1')
        self.portal.invokeFactory('Folder', 'folder2')
        folder2 = getattr(self.portal, 'folder2')
        self.setRoles(['Member'])

    def testCreateTopLevelTabs(self):
        # See if we can create one at all
        tabs = self.utils.createTopLevelTabs()
        self.failUnless(tabs)
        #Only the folders show up (Members, news, folder1, folder2)
        self.assertEqual(len(tabs), 5)

    def testTabsRespectFolderOrder(self):
        # See if reordering causes a change in the tab order
        tabs1 = self.utils.createTopLevelTabs()
        self.portal.moveObjectsByDelta('folder2', -1)
        tabs2 = self.utils.createTopLevelTabs()
        #Same number of objects
        self.failUnlessEqual(len(tabs1), len(tabs2))
        #Different order
        self.failUnless(tabs1 != tabs2)

    def testCustomQuery(self):
        # Try a custom query script for the tabs that returns only published
        # objects
        workflow = self.portal.portal_workflow
        factory = self.portal.manage_addProduct['PythonScripts']
        factory.manage_addPythonScript('getCustomNavQuery')
        script = self.portal.getCustomNavQuery
        script.ZPythonScript_edit('','return {"review_state":"published"}')
        self.assertEqual(self.portal.getCustomNavQuery(),{"review_state":"published"})
        tabs = self.utils.createTopLevelTabs()
        #Should contain no folders
        self.assertEqual(len(tabs), 0)
        #change workflow for folder1
        workflow.doActionFor(self.portal.folder1, 'publish')
        self.portal.folder1.reindexObject()
        tabs = self.utils.createTopLevelTabs()
        #Should only contain current object and published folder
        self.assertEqual(len(tabs), 1)

    def testDisableFolderTabs(self):
        # Setting the site_property disable_folder_sections should remove
        # all folder based tabs
        props = self.portal.portal_properties.site_properties
        props.manage_changeProperties(disable_folder_sections=True)
        tabs = self.utils.createTopLevelTabs()
        self.assertEqual(tabs, [])

    def testTabsExcludeItemsWithExcludeProperty(self):
        # Make sure that items witht he exclude_from_nav property are purged
        self.portal.folder2.manage_addProperty('exclude_from_nav',True,'boolean')
        self.portal.folder2.reindexObject()
        tabs = self.utils.createTopLevelTabs()
        self.failUnless(tabs)
        self.assertEqual(len(tabs),4)
        tab_names = [t['id'] for t in tabs]
        self.failIf('folder2' in tab_names)

    def testTabsRespectsTypesWithViewAction(self):
        # With a type in typesUseViewActionInListings as current action it
        # should return a tab which has '/view' appended to the url
        tabs = self.utils.createTopLevelTabs()
        self.failUnless(tabs)
        # Fail if 'view' is used for folder
        self.failIf(tabs[-1]['url'][-5:]=='/view')
        # Add Folder to site_property
        props = self.portal.portal_properties.site_properties
        props.manage_changeProperties(typesUseViewActionInListings=['Image','File','Folder'])
        # Verify that we have '/view'
        tabs = self.utils.createTopLevelTabs()
        self.failUnless(tabs)
        self.assertEqual(tabs[-1]['url'][-5:],'/view')

    def testTabsExcludeItemsInIdsNotToList(self):
        # Make sure that items whose ids are in the idsNotToList navTree
        # property get purged
        ntp=self.portal.portal_properties.navtree_properties
        ntp.manage_changeProperties(idsNotToList=['folder2'])
        tabs = self.utils.createTopLevelTabs()
        self.failUnless(tabs)
        self.assertEqual(len(tabs),4)
        tab_names = [t['id'] for t in tabs]
        self.failIf('folder2' in tab_names)


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
        self.failUnless(crumbs)
        self.assertEqual(len(crumbs), 2)
        self.assertEqual(crumbs[-1]['absolute_url'], doc.absolute_url())
        self.assertEqual(crumbs[-2]['absolute_url'], doc.aq_parent.absolute_url())

    def testBreadcrumbsRespectTypesWithViewAction(self):
        # With a type in typesUseViewActionInListings as current action it
        # should return a breadcrumb which has '/view' appended to the url
        file = self.portal.folder1.file11
        crumbs = self.utils.createBreadCrumbs(file)
        self.failUnless(crumbs)
        self.assertEqual(crumbs[-1]['absolute_url'][-5:],'/view')


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestPloneTool))
    suite.addTest(makeSuite(TestOwnershipStuff))
    suite.addTest(makeSuite(TestEditMetadata))
    suite.addTest(makeSuite(TestEditMetadataIndependence))
    suite.addTest(makeSuite(TestFormulatorFields))
    suite.addTest(makeSuite(TestNavTree))
    suite.addTest(makeSuite(TestPortalTabs))
    suite.addTest(makeSuite(TestBreadCrumbs))
    return suite

if __name__ == '__main__':
    framework()
