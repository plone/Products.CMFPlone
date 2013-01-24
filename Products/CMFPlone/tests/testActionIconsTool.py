from Products.CMFPlone.tests import PloneTestCase


class TestActionIconsTool(PloneTestCase.PloneTestCase):

    def afterSetUp(self):
        self.actionicons = self.portal.portal_actionicons
        self._refreshSkinData()

    def testAddActionIcon(self):
        length = len(self.actionicons.listActionIcons())
        self.actionicons.addActionIcon('content_actions',
                                       'preview',
                                       'lock_icon.png',
                                       title='preview')
        action_icons = self.actionicons.listActionIcons()
        preview = action_icons[-1]
        self.assertEqual(len(action_icons), length + 1)
        self.assertEqual(preview._category, 'content_actions')
        self.assertEqual(preview._action_id, 'preview')
        self.assertEqual(preview._title, 'preview')

    def testRenderActionIcon(self):
        self.testAddActionIcon()
        icon = self.actionicons.renderActionIcon('content_actions',
                                                 'preview')
        obj = self.portal.restrictedTraverse('lock_icon.png')
        self.assertEqual(obj, icon)

    def testRenderDefaultActionIcon(self):
        icon = self.actionicons.renderActionIcon('content_actions',
                                                 'doesnotexist',
                                                 default='document_icon.png')
        obj = self.portal.restrictedTraverse('document_icon.png')
        self.assertEqual(obj, icon)

    def testRenderNoneActionIcon(self):
        icon = self.actionicons.renderActionIcon('content_actions',
                                                 'doesnotexist',
                                                 None)
        self.assertEqual(icon, None)
