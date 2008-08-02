#
# MemberDataTool tests
#

from Products.CMFPlone.tests import PloneTestCase
from Products.CMFPlone.tests import dummy

from DateTime import DateTime

from OFS.Image import Image
default_user = PloneTestCase.default_user


class TestMemberDataTool(PloneTestCase.PloneTestCase):

    def afterSetUp(self):
        self.memberdata = self.portal.portal_memberdata
        self.membership = self.portal.portal_membership
        self.membership.memberareaCreationFlag = 0
        # Don't let default_user disturb results
        self.portal.acl_users._doDelUsers([default_user])
        # Add some members
        self.addMember('fred', 'Fred Flintstone', 'fred@bedrock.com', ['Member', 'Reviewer'], '2002-01-01')
        self.addMember('barney', 'Barney Rubble', 'barney@bedrock.com', ['Member'], '2002-01-01')
        self.addMember('brubble', 'Bambam Rubble', 'bambam@bambam.net', ['Member'], '2003-12-31')
        # MUST reset this
        self.memberdata._v_temps = None

    def addMember(self, username, fullname, email, roles, last_login_time):
        self.membership.addMember(username, 'secret', roles, [])
        member = self.membership.getMemberById(username)
        member.setMemberProperties({'fullname': fullname, 'email': email,
                                    'last_login_time': DateTime(last_login_time),})

    def testSetPortrait(self):
        self.memberdata._setPortrait(Image(id=default_user, file=dummy.File(), title=''), default_user)
        self.assertEqual(self.memberdata._getPortrait(default_user).getId(), default_user)
        self.assertEqual(self.memberdata._getPortrait(default_user).meta_type, 'Image')

    def testDeletePortrait(self):
        self.memberdata._setPortrait(Image(id=default_user, file=dummy.File(), title=''), default_user)
        self.memberdata._deletePortrait(default_user)
        self.assertEqual(self.memberdata._getPortrait(default_user), None)

    def testPruneMemberDataContents(self):
        # Only test what is not already tested elswhere
        self.memberdata._setPortrait(Image(id=default_user, file=dummy.File(), title=''), default_user)
        self.memberdata._setPortrait(Image(id=default_user, file=dummy.File(), title=''), 'dummy')
        self.memberdata.pruneMemberDataContents()
        self.assertEqual(len(self.memberdata.portraits.objectIds()), 1)

    def testFulltextMemberSearch(self):
        # Search for a user by id, name, email, ...
        search = self.memberdata.searchFulltextForMembers
        self.assertEqual(len(search('')), 3)
        self.assertEqual(len(search('rubble')), 2)
        self.assertEqual(len(search('stone')), 1)
        self.assertEqual(len(search('bambam.net')), 1)
        self.assertEqual(len(search('bedrock.com')), 2)
        self.assertEqual(len(search('brubble')), 1)


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestMemberDataTool))
    return suite
