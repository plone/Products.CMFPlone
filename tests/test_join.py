""" 
Tests for joining/registration of a user.

$Id: test_join.py,v 1.1.2.1 2002/10/07 14:34:24 dreamcatcher Exp $
"""

import Zope
from unittest import TestSuite, makeSuite, main

from Products.CMFCore.tests.base.testcase import \
     TransactionalTest

class MembershipTests( TransactionalTest ):

    def setUp(self):
        TransactionalTest.setUp(self)
        self.root.manage_addProduct[ 'CMFPlone' ].manage_addSite( 'site' )

    def test_join( self ):
        site = self.root.site
        site.portal_membership.memberareaCreationFlag = 0
        member_id = 'test_user'
        site.portal_registration.addMember( member_id
                                          , 'zzyyzz'
                                          , properties={ 'username': member_id
                                                       , 'email' : 'foo@bar.com'
                                                       }
                                          )
        u = site.acl_users.getUser(member_id)
        self.failUnless(u)
        self.assertRaises(AttributeError,
                          getattr, site.Members, member_id)
        # test that wrapUser correctly creates member area
        site.portal_membership.setMemberareaCreationFlag()
        site.portal_membership.wrapUser(u)
        memberfolder = getattr(site.Members, member_id)
        homepage = memberfolder.index_html
        self.assertEqual( memberfolder.Title(), "test_user's Home" )
        tool = site.portal_workflow
        self.assertEqual( tool.getInfoFor( homepage, 'review_state' )
                        , "visible" )

    def test_join_without_email( self ):
        site = self.root.site
        self.assertRaises(ValueError,
                          site.portal_registration.addMember,
                          'test_user',
                          'zzyyzz',
                          properties={'username':'test_user', 'email': ''}
                          )

def test_suite():
    return TestSuite((
        makeSuite(MembershipTests),
        ))

if __name__ == '__main__':
    main(defaultTest='test_suite')
