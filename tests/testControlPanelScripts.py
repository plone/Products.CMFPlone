#
# Tests the control panel scripts
#

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase
from Products.CMFPlone.tests import PloneTestCase
from Products.CMFPlone.tests import dummy

from DateTime import DateTime
from zope.app.tests.placelesssetup import setUp, tearDown

class TestPrefsUserManage(PloneTestCase.PloneTestCase):

    def afterSetUp(self):
        setUp()
        self.membership = self.portal.portal_membership
        self.membership.memberareaCreationFlag = 0

    def addMember(self, username, fullname, email, roles, last_login_time):
        self.membership.addMember(username, 'secret', roles, [])
        member = self.membership.getMemberById(username)
        member.setMemberProperties({'fullname': fullname, 'email': email,
                                    'last_login_time': DateTime(last_login_time),})

    def test_bug4333_delete_user_remove_memberdata(self):
        # delete user should delete portal_memberdata
        memberdata = self.portal.portal_memberdata
        self.setRoles(['Manager'])
        self.addMember('barney', 'Barney Rubble', 'barney@bedrock.com', ['Member'], '2002-01-01')
        barney = self.membership.getMemberById('barney')
        self.failUnlessEqual(barney.email, 'barney@bedrock.com')
        del barney

        self.portal.prefs_user_manage(delete=['barney'])
        md = memberdata._members
        self.failIf(md.has_key('barney'))

        # There is an _v_ variable that is killed at the end of each request
        # which stores a temporary version of the member object, this is
        # a problem in this test.
        memberdata._v_temps = None

        self.membership.addMember('barney', 'secret', ['Members'], [])
        barney = self.membership.getMemberById('barney')
        self.failIfEqual(barney.fullname, 'Barney Rubble')
        self.failIfEqual(barney.email, 'barney@bedrock.com')

    def beforeTearDown(self):
        tearDown()


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestPrefsUserManage))
    return suite

if __name__ == '__main__':
    framework()
