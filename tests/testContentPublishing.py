#
# Tests security of content publishing operations
# code inspired by Ween
#

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase
from Products.CMFPlone.tests import PloneTestCase

from AccessControl import Unauthorized, getSecurityManager
from Acquisition import aq_base
from DateTime import DateTime
from StringIO import StringIO

text="""I lick my brain in silence
Rather squeeze my head instead
Midget man provoking violence
Listen not to what I said 

I said please calm it down
Everything is turning brown

Mutilated lips give a kiss on the wrist
Of the worm like tips of tentacles expanding
In my mind, I'm fine, accepting only fresh brine
You can get another drop of this, yeah you wish...
[repeat]

Laughing lady living lover
Ooo you sassy frassy lassie
Find me the skull of Haile Sellase, I...
Give me shoes so I can tapsy
Tap all over this big world
Take my hand you ugly girl """

props={'description':'song by ween',
       'contributors':['dean ween', 'gean ween'],
       'effective_date':'1/12/2004',
       'expiration_date':'12/12/2004',
       'format':'text/plain',
       'language':'english',
       'rights':'ween music',
       'title':'mutalitated lips',
       'subject':['psychedelic', 'pop', '13th floor elevators']}

class TestContentPublishing(PloneTestCase.PloneTestCase):

    def afterSetUp(self):
        self.portal.acl_users._doAddUser('user1', 'secret', ['Member'], [])
        self.membership = self.portal.portal_membership
        self.createMemberarea('user1')

    def _checkMD(self, obj, **changes):
        """ check the DublinCore Metadata on obj - it must inherient from DublinCore """
        if changes:
            _orig_props = {}
            _orig_props.update(props)
            props.update(changes)
            
        self.failUnless(obj.Title() == props['title'])
        self.failUnless(obj.Description() == props['description'])
        self.failUnless(obj.Subject() == tuple(props['subject']))
        self.failUnless(obj.ExpirationDate() == obj._datify(props['expiration_date']).ISO())
        self.failUnless(obj.EffectiveDate() == obj._datify(props['effective_date']).ISO())
        self.failUnless(obj.Format() == props['format'])
        self.failUnless(obj.Rights() == props['rights'])
        self.failUnless(obj.Language() == props['language'])
        self.failUnless(obj.Contributors() == tuple(props['contributors']))

        if changes:
            props.update(_orig_props)

    def testInstaPublishing(self):
        """ The instant publishing drop down UI.
            !NOTE! CMFDefault.Document overrides setFormat and Format
            so it acts strangely.  This is also hardcoded to work with
            CMFDefault.Document.

            This test was written to prevent collector/2914 regressions
            XXX This test should be fixed for 2.1
            
        """
        self.folder.invokeFactory('Document', id='mollusk')
        get_transaction().commit(1)
        mollusk=self.folder.mollusk
        mollusk.document_edit('plain', text, title=props['title'])
        self.failUnless(mollusk.CookedBody()!=text)
        mollusk.metadata_edit(**props)
        self._checkMD(mollusk)
        mollusk.content_status_modify(workflow_action='submit')
        self._checkMD(mollusk)
        mollusk.content_status_modify(workflow_action='retract')
        self._checkMD(mollusk)

        self.folder.invokeFactory('File', id='lyrics.txt')
        _file = StringIO(text)
        _file.filename='lyrics.txt'
        lyrics = self.folder['lyrics.txt']
        lyrics.file_edit(file=_file)
        lyrics.metadata_edit(**props)
        self._checkMD(lyrics)
        lyrics.content_status_modify(workflow_action='submit')
        self._checkMD(lyrics)
        
        _file = StringIO(text)
        _file.filename='lyrics.doc'
        self.folder.invokeFactory('File', id='lyrics.doc')
        lyrics = self.folder['lyrics.doc']
        lyrics.file_edit(file=_file)
        self.failUnless(lyrics.Format()=='application/msword')
        lyrics.metadata_edit(description='great song')
        self.failUnless(lyrics.Format()=='application/msword')
        lyrics.content_status_modify(workflow_action='submit')
        self.failUnless(lyrics.Format()=='application/msword')


        
if __name__ == '__main__':
    framework()
else:
    def test_suite():
        from unittest import TestSuite, makeSuite
        suite = TestSuite()
        suite.addTest(makeSuite(TestContentPublishing))
        return suite
