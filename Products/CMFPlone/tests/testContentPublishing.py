#
# Tests security of content publishing operations
# code inspired by Ween
#

from Products.CMFPlone.tests import PloneTestCase

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
       'contributors':['dean ween', 'gene ween'],
       'effective_date':'2004-01-12',
       'expiration_date':'2004-12-12',
       'format':'text/plain',
       'language':'english',
       'rights':'ween music',
       'title':'mutalitated lips',
       'subject':['psychedelic', 'pop', '13th floor elevators']}


class TestContentPublishing(PloneTestCase.PloneTestCase):
    """ The instant publishing drop down UI.
        !NOTE! CMFDefault.Document overrides setFormat and Format
        so it acts strangely.  This is also hardcoded to work with Document.

        This testcase was written to prevent collector/2914 regressions

        In addition, some more general tests of content_status_modify and
        folder_publish behaviour have been added, since this seems a logical
        place to keep them.
    """

    def afterSetUp(self):
        self.portal.acl_users._doAddUser('user1', 'secret', ['Member'], [])
        self.membership = self.portal.portal_membership
        self.createMemberarea('user1')
        self.workflow = self.portal.portal_workflow
        self.setupAuthenticator()

    def _checkMD(self, obj, **changes):
        """ check the DublinCore Metadata on obj - it must inherit from DublinCore """
        if changes:
            _orig_props = {}
            _orig_props.update(props)
            props.update(changes)

        self.assertEqual(obj.Title(), props['title'])
        self.assertEqual(obj.Description(), props['description'])
        self.assertEqual(obj.Subject(), tuple(props['subject']))
        self.assertEqual(obj.ExpirationDate(zone='UTC'),
                         obj._datify(props['expiration_date']).ISO())
        self.assertEqual(obj.EffectiveDate(zone='UTC'),
                         obj._datify(props['effective_date']).ISO())
        self.assertEqual(obj.Format(), props['format'])
        self.assertEqual(obj.Rights(), props['rights'])
        self.assertEqual(obj.Language(), props['language'])
        self.assertEqual(obj.Contributors(), tuple(props['contributors']))

        if changes:
            props.update(_orig_props)

    # Test the recursive behaviour of content_status_modify and folder_publish:

    def testPublishingSubobjects(self):
        self.setRoles(['Manager']) # Make sure we can publish directly
        self.folder.invokeFactory('Document', id = 'd1', title = 'Doc 1')
        self.folder.invokeFactory('Folder', id = 'f1', title = 'Folder 1')
        self.folder.f1.invokeFactory('Document', id = 'd2', title = 'Doc 2')
        self.folder.f1.invokeFactory('Folder', id = 'f2', title = 'Folder 2')
        paths = []
        for o in (self.folder.d1, self.folder.f1):
            paths.append('/'.join(o.getPhysicalPath()))

        # folder_publish requires a non-GET request
        self.setRequestMethod('POST')
        self.folder.folder_publish(workflow_action = 'publish',
                                   paths = paths,
                                   include_children = True)
        for o in (self.folder.d1, self.folder.f1, self.folder.f1.d2, self.folder.f1.f2):
            self.assertEqual(self.workflow.getInfoFor(o, 'review_state'),'published')

    def testPublishingSubobjectsAndExpireThem(self):
        self.setRoles(['Manager']) # Make sure we can publish directly
        self.folder.invokeFactory('Document', id = 'd1', title = 'Doc 1')
        self.folder.invokeFactory('Folder', id = 'f1', title = 'Folder 1')
        self.folder.f1.invokeFactory('Document', id = 'd2', title = 'Doc 2')
        self.folder.f1.invokeFactory('Folder', id = 'f2', title = 'Folder 2')
        paths = []
        for o in (self.folder.d1, self.folder.f1):
            paths.append('/'.join(o.getPhysicalPath()))

        # folder_publish requires a non-GET request
        self.setRequestMethod('POST')
        self.folder.folder_publish(workflow_action = 'publish',
                                   paths = paths,
                                   effective_date = '1/1/2001',
                                   expiration_date = '1/2/2001',
                                   include_children = True)
        for o in (self.folder.d1, self.folder.f1, self.folder.f1.d2, self.folder.f1.f2):
            self.assertEqual(self.workflow.getInfoFor(o, 'review_state'),'published')
            self.failUnless(self.portal.isExpired(o))

    def testPublishingWithoutSubobjects(self):
        self.setRoles(['Manager']) # Make sure we can publish directly
        self.folder.invokeFactory('Document', id = 'd1', title = 'Doc 1')
        self.folder.invokeFactory('Folder', id = 'f1', title = 'Folder 1')
        self.folder.f1.invokeFactory('Document', id = 'd2', title = 'Doc 2')
        self.folder.f1.invokeFactory('Folder', id = 'f2', title = 'Folder 2')
        paths = []
        for o in (self.folder.d1, self.folder.f1):
            paths.append('/'.join(o.getPhysicalPath()))

        # folder_publish requires a non-GET request
        self.setRequestMethod('POST')
        self.folder.folder_publish(workflow_action = 'publish',
                                   paths = paths,
                                   include_children = False)
        for o in (self.folder.d1, self.folder.f1):
            self.assertEqual( self.workflow.getInfoFor(o, 'review_state'), 'published')
        for o in (self.folder.f1.d2, self.folder.f1.f2):
            self.assertEqual( self.workflow.getInfoFor(o, 'review_state'), 'visible')

    def testPublishingNonDefaultPageLeavesFolderAlone(self):
        self.setRoles(['Manager']) # Make sure we can publish directly
        self.folder.invokeFactory('Document', id = 'd1', title = 'Doc 1')
        self.folder.d1.content_status_modify('publish')
        self.assertEqual(self.workflow.getInfoFor(self.folder, 'review_state'), 'visible')
        self.assertEqual(self.workflow.getInfoFor(self.folder.d1, 'review_state'), 'published')

    def testPublishingDefaultPagePublishesFolder(self):
        self.setRoles(['Manager']) # Make sure we can publish directly
        self.folder.invokeFactory('Document', id = 'd1', title = 'Doc 1')
        self.folder.setDefaultPage('d1')
        self.folder.d1.content_status_modify('publish')
        self.assertEqual(self.workflow.getInfoFor(self.folder, 'review_state'), 'published')
        self.assertEqual(self.workflow.getInfoFor(self.folder.d1, 'review_state'), 'published')

    def testPublishingDefaultPageWhenFolderCannotBePublished(self):
        self.setRoles(['Manager']) # Make sure we can publish directly
        self.folder.invokeFactory('Document', id = 'd1', title = 'Doc 1')
        self.folder.setDefaultPage('d1')
        # make parent be published already when publishing its default document
        # results in an attempt to do it again
        self.folder.content_status_modify('publish')
        self.assertEqual(self.workflow.getInfoFor(self.folder, 'review_state'), 'published')
        self.folder.d1.content_status_modify('publish')
        self.assertEqual(self.workflow.getInfoFor(self.folder, 'review_state'), 'published')
        self.assertEqual(self.workflow.getInfoFor(self.folder.d1, 'review_state'), 'published')

    # test setting effective/expiration date and isExpired script

    def testIsExpiredWithExplicitExpiredContent(self):
        self.setRoles(['Manager'])
        self.folder.invokeFactory('Document', id = 'd1', title = 'Doc 1')
        self.folder.d1.content_status_modify(workflow_action = 'publish',
                                             effective_date = '1/1/2001',
                                             expiration_date = '1/2/2001')
        self.failUnless(self.portal.isExpired(self.folder.d1))

    def testIsExpiredWithImplicitExpiredContent(self):
        self.setRoles(['Manager'])
        self.folder.invokeFactory('Document', id = 'd1', title = 'Doc 1')
        self.folder.d1.content_status_modify(workflow_action = 'publish',
                                             effective_date = '1/1/2001',
                                             expiration_date = '1/2/2001')
        self.failUnless(self.folder.d1.isExpired())

    def testIsExpiredWithExplicitNonExpiredContent(self):
        self.setRoles(['Manager'])
        self.folder.invokeFactory('Document', id = 'd1', title = 'Doc 1')
        self.folder.d1.content_status_modify(workflow_action = 'publish')
        self.failIf(self.portal.isExpired(self.folder.d1))

    def testIsExpiredWithImplicitNonExpiredContent(self):
        self.setRoles(['Manager'])
        self.folder.invokeFactory('Document', id = 'd1', title = 'Doc 1')
        self.folder.d1.content_status_modify(workflow_action = 'publish')
        self.failIf(self.folder.d1.isExpired())


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestContentPublishing))
    return suite
