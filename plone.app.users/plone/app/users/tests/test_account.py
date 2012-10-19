import unittest
from Testing.makerequest import makerequest
from OFS.SimpleItem import SimpleItem

from plone.app.users.browser.account import AccountPanelSchemaAdapter


class DummyPortalMembership(object):

    def __init__(self, allowed):
        self.allowed = allowed

    def getMemberById(self, id):
        return id

    def getAuthenticatedMember(self):
        return '(authenticated)'

    def checkPermission(self, permission, context):
        return self.allowed


class TestAccountPanelSchemaAdapter(unittest.TestCase):

    def test__init__no_userid(self):
        # should edit current user
        context = makerequest(SimpleItem('foo'))
        context.portal_membership = DummyPortalMembership(False)
        adapter = AccountPanelSchemaAdapter(context)
        self.assertEqual('(authenticated)', adapter.context)

    def test__init__userid_in_request_form_for_non_manager(self):
        # disallow for non-privileged users
        context = makerequest(SimpleItem('foo'))
        context.portal_membership = DummyPortalMembership(False)
        context.REQUEST.form['userid'] = 'bob'
        adapter = AccountPanelSchemaAdapter(context)
        self.assertEqual('(authenticated)', adapter.context)

    def test__init__userid_in_request_form_for_manager(self):
        # should allow for privileged users
        context = makerequest(SimpleItem('foo'))
        context.portal_membership = DummyPortalMembership(True)
        context.REQUEST.form['userid'] = 'bob'
        adapter = AccountPanelSchemaAdapter(context)
        self.assertEqual('bob', adapter.context)
