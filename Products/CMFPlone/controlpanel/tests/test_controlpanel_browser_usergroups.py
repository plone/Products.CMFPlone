from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.testing.zope import Browser
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.testing import PRODUCTS_CMFPLONE_FUNCTIONAL_TESTING
from Products.CMFPlone.utils import normalizeString

import transaction
import unittest


class UserGroupsControlPanelFunctionalTest(unittest.TestCase):
    """Test that changes in the user groups control panel are actually
    creating and changing users and groups.
    """

    layer = PRODUCTS_CMFPLONE_FUNCTIONAL_TESTING

    def _generateGroups(self):
        groupsTool = getToolByName(self.portal, "portal_groups")
        self.groups = [
            {"id": "group1", "title": "Group 1"},
            {"id": "group2", "title": "Group 2"},
            {"id": "group3", "title": "Group 3 accentué"},
        ]
        for group in self.groups:
            groupsTool.addGroup(group["id"], [], [], title=group["title"])

    def _generateUsers(self):
        self.members = [
            {
                "username": "DIispfuF",
                "fullname": "Kevin Hughes",
                "email": "DIispfuF@example.com",
            },
            {
                "username": "enTHXigm",
                "fullname": "Richard Ramirez",
                "email": "enTHXigm@example.com",
            },
            {
                "username": "q7UsYcrT",
                "fullname": "Kyle Brown",
                "email": "q7UsYcrT@example.com",
            },
            {
                "username": "j5g0xPmr",
                "fullname": "Julian Green",
                "email": "j5g0xPmr@example.com",
            },
            {
                "username": "o6Sx4It3",
                "fullname": "Makayla Coleman",
                "email": "o6Sx4It3@example.com",
            },
            {
                "username": "SLUhquYa",
                "fullname": "Sean Foster",
                "email": "SLUhquYa@example.com",
            },
            {
                "username": "nHWl3Ita",
                "fullname": "Molly Martin",
                "email": "nHWl3Ita@example.com",
            },
            {
                "username": "xdkpCKmX",
                "fullname": "Jordan Thompson",
                "email": "xdkpCKmX@example.com",
            },
            {
                "username": "p8H6CicB",
                "fullname": "Tyler Rivera",
                "email": "p8H6CicB@example.com",
            },
            {
                "username": "T6vdBXbD",
                "fullname": "Megan Murphy",
                "email": "T6vdBXbD@example.com",
            },
            {
                "username": "DohPmgIa",
                "fullname": "Gracie Diaz",
                "email": "DohPmgIa@example.com",
            },
            {
                "username": "CqHWi65B",
                "fullname": "Rachel Morgan",
                "email": "CqHWi65B@example.com",
            },
            {
                "username": "uHFQ7qk4",
                "fullname": "Maya Price",
                "email": "uHFQ7qk4@example.com",
            },
            {
                "username": "BlXLQh7r",
                "fullname": "Blake Jenkins",
                "email": "BlXLQh7r@example.com",
            },
            {
                "username": "FCrWUiSY",
                "fullname": "Owen Ramirez",
                "email": "FCrWUiSY@example.com",
            },
            {
                "username": "bX3PqgHK",
                "fullname": "Owen Cook",
                "email": "bX3PqgHK@example.com",
            },
            {
                "username": "sD35vVl0",
                "fullname": "Jayden Hill",
                "email": "sD35vVl0@example.com",
            },
            {
                "username": "mfOcjXAG",
                "fullname": "Joseph Ramirez",
                "email": "mfOcjXAG@example.com",
            },
            {
                "username": "GAJtdYbM",
                "fullname": "Nathan Young",
                "email": "GAJtdYbM@example.com",
            },
            {
                "username": "E1OWG6bv",
                "fullname": "Kaitlyn Hernandez",
                "email": "E1OWG6bv@example.com",
            },
            {
                "username": "BqOX2sCm",
                "fullname": "Faith Price",
                "email": "BqOX2sCm@example.com",
            },
            {
                "username": "tyOxRnml",
                "fullname": "Sofia Williams",
                "email": "5yOxRjtl@example.com",
            },
            {
                "username": "fVcumDNl",
                "fullname": "David Sanders",
                "email": "fVcumDNl@example.com",
            },
            {
                "username": "Ge1hqdEI",
                "fullname": "Jack Simmons",
                "email": "Ge1hqdEI@example.com",
            },
            {
                "username": "o2CqT7kG",
                "fullname": "Cole Howard",
                "email": "o2CqT7kG@example.com",
            },
            {
                "username": "mpGtfNl6",
                "fullname": "Rachel Miller",
                "email": "mpGtfNl6@example.com",
            },
            {
                "username": "RGrpWiBg",
                "fullname": "Henry Patterson",
                "email": "RGrpWiBg@example.com",
            },
            {
                "username": "Bufmi0YS",
                "fullname": "Avery Cooper",
                "email": "Bufmi0YS@example.com",
            },
            {
                "username": "J7NvbjYd",
                "fullname": "Sydney Bennett",
                "email": "J7NvbjYd@example.com",
            },
            {
                "username": "u5Xem8U1",
                "fullname": "Daniel Johnson",
                "email": "u5Xem8U1@example.com",
            },
            {
                "username": "TWrMCLIo",
                "fullname": "Autumn Brooks",
                "email": "0VrMCLIo@example.com",
            },
            {
                "username": "FElYwiIr",
                "fullname": "Alexandra Nelson",
                "email": "FElYwiIr@example.com",
            },
            {
                "username": "teK6pkhc",
                "fullname": "Brian Simmons",
                "email": "0eK6pkhc@example.com",
            },
            {
                "username": "RwAO2YPa",
                "fullname": "Kevin Hughes",
                "email": "gracie@example.com",
            },
            {
                "username": "nlBMw26i",
                "fullname": "Sydney Evans",
                "email": "nlBMw26i@example.com",
            },
            {
                "username": "Ahr3EiRC",
                "fullname": "Emma Brown",
                "email": "Ahr3EiRC@example.com",
            },
            {
                "username": "NhuU0Y5x",
                "fullname": "Lauren Martin",
                "email": "NhuU0Y5x@example.com",
            },
            {
                "username": "j2R3mKQg",
                "fullname": "Isabelle Russell",
                "email": "j2R3mKQg@example.com",
            },
            {
                "username": "qOmK0iCN",
                "fullname": "Anna Baker",
                "email": "qOmK0iCN@example.com",
            },
            {
                "username": "uQbVOgo7",
                "fullname": "Brady Watson",
                "email": "uQbVOgo7@example.com",
            },
            {
                "username": "oLDCaQfW",
                "fullname": "Kaitlyn Robinson",
                "email": "oLDCaQfW@example.com",
            },
            {
                "username": "osYHeFD1",
                "fullname": "Riley Richardson",
                "email": "osYHeFD1@example.com",
            },
            {
                "username": "i4pHduDY",
                "fullname": "Kayla Sanders",
                "email": "i4pHduDY@example.com",
            },
            {
                "username": "BvyX6qF3",
                "fullname": "Sara Richardson",
                "email": "BvyX6qF3@example.com",
            },
            {
                "username": "a3EpwDYj",
                "fullname": "Trinity Gonzales",
                "email": "a3EpwDYj@example.com",
            },
            {
                "username": "JDMseWdt",
                "fullname": "Madeline Garcia",
                "email": "JDMseWdt@example.com",
            },
            {
                "username": "lPCYBvoi",
                "fullname": "Brian Gray",
                "email": "lPCYBvoi@example.com",
            },
            {
                "username": "AByCsRQ3",
                "fullname": "Victoria Perez",
                "email": "AByCsRQ3@example.com",
            },
            {
                "username": "CH7uVlNy",
                "fullname": "Charles Rodriguez",
                "email": "5H7uVlNy@example.com",
            },
            {
                "username": "XYsmd7ux",
                "fullname": "Abigail Simmons",
                "email": "XYsmd7ux@example.com",
            },
            {
                "username": "DfaA1wqC3",
                "fullname": "Émilie Richard",
                "email": "DfaA1wqC3@example.com",
            },
        ]
        rtool = getToolByName(self.portal, "portal_registration")
        for member in self.members:
            rtool.addMember(member["username"], "somepassword", properties=member)

    def setUp(self):
        self.app = self.layer["app"]
        self.portal = self.layer["portal"]
        self.portal_url = self.portal.absolute_url()
        self.users_url = "%s/@@usergroup-userprefs" % self.portal_url
        self.groups_url = "%s/@@usergroup-groupprefs" % self.portal_url
        self.settings_url = "%s/@@usergroup-controlpanel" % self.portal_url
        self.memberfields_url = "%s/@@member-fields" % self.portal_url
        self._generateGroups()
        self._generateUsers()
        transaction.commit()

        self.browser = Browser(self.app)
        self.browser.handleErrors = False
        self.browser.addHeader(
            "Authorization", f"Basic {SITE_OWNER_NAME}:{SITE_OWNER_PASSWORD}"
        )

    def test_usergroups_control_panel_link_users(self):
        self.browser.open("%s/@@overview-controlpanel" % self.portal_url)
        # There are two Users links.  The first is the Users tab.
        # We need to open the second one.
        self.browser.getLink("Users", index=1).click()
        self.assertEqual(self.browser.url, self.users_url)

    def test_usergroups_control_panel_link_groups(self):
        self.browser.open("%s/@@overview-controlpanel" % self.portal_url)
        self.browser.getLink("Groups").click()
        self.assertEqual(self.browser.url, self.groups_url)

    def test_usergroups_control_panel_link_settings_user_groups(self):
        self.browser.open("%s/@@overview-controlpanel" % self.portal_url)
        self.browser.getLink("User and Group Settings").click()
        self.assertEqual(self.browser.url, self.settings_url)

    def test_usergroups_control_panel_link_settings_member_fields(self):
        self.browser.open("%s/@@overview-controlpanel" % self.portal_url)
        self.browser.getLink("Member Fields").click()
        self.assertEqual(self.browser.url, self.memberfields_url)

    def test_user_search_by_name(self):
        self.browser.open(self.users_url)
        self.browser.getControl(name="searchstring").value = "Richard"
        self.browser.getControl(name="form.button.Search").click()
        self.assertIn("Richard Ramirez", self.browser.contents)
        self.assertIn("Sara Richardson", self.browser.contents)
        self.assertIn("Émilie Richard", self.browser.contents)

    def test_user_search_by_name_accent(self):
        self.browser.open(self.users_url)
        self.browser.getControl(name="searchstring").value = "Émilie"
        self.browser.getControl(name="form.button.Search").click()
        self.assertIn("Émilie Richard", self.browser.contents)

    def test_user_search_by_id(self):
        self.browser.open(self.users_url)
        self.browser.getControl(name="searchstring").value = "TWrMCLIo"
        self.browser.getControl(name="form.button.Search").click()
        self.assertIn("Autumn Brooks", self.browser.contents)

    def test_user_search_by_mail(self):
        self.browser.open(self.users_url)
        self.browser.getControl(name="searchstring").value = "DohPmgIa@"
        self.browser.getControl(name="form.button.Search").click()
        self.assertIn("Gracie Diaz", self.browser.contents)

    def test_user_show_all(self):
        self.browser.open(self.users_url)
        self.browser.getControl(name="form.button.FindAll").click()

        # Check that first 10 members (sorted by fullname) are shown.
        for member in sorted(
            self.members, key=lambda k: normalizeString(k["fullname"])
        )[:10]:
            self.assertIn(member["fullname"], self.browser.contents)

    def test_user_show_all_with_search_term(self):
        self.browser.open(self.users_url)
        self.browser.getControl(name="searchstring").value = "no-user"
        self.browser.getControl(name="form.button.FindAll").click()

        # Check that all members is shown and search term is ignored
        self.assertIn("Avery Cooper", self.browser.contents)

    def test_user_add_new_link(self):
        self.browser.open(self.users_url)
        self.browser.getLink(id="add-user").click()
        self.assertEqual(self.browser.url, "%s/@@new-user" % self.portal_url)

    def test_user_modify_roles(self):
        self.browser.open(self.users_url)
        self.browser.getControl(name="searchstring").value = "TWrMCLIo"
        self.browser.getControl(name="form.button.Search").click()

        # Check that contributor role is not enabled and enable it
        self.assertFalse(
            self.browser.getControl(name="users.roles:list:records")
            .getControl(value="Contributor")
            .selected
        )
        self.browser.getControl(name="users.roles:list:records").getControl(
            value="Contributor"
        ).selected = True
        self.browser.getControl(name="form.button.Modify").click()

        # Check that contributor role is now enabled for this user
        self.browser.open(self.users_url)
        self.browser.getControl(name="searchstring").value = "TWrMCLIo"
        self.browser.getControl(name="form.button.Search").click()
        self.assertTrue(
            self.browser.getControl(name="users.roles:list:records")
            .getControl(value="Contributor")
            .selected
        )

    def test_user_delete(self):
        self.browser.open(self.users_url)
        self.browser.getControl(name="searchstring").value = "TWrMCLIo"
        self.browser.getControl(name="form.button.Search").click()
        self.assertIn("Autumn Brooks", self.browser.contents)

        # Delete user
        self.browser.getControl(name="delete:list").getControl(
            value="TWrMCLIo"
        ).selected = True
        self.browser.getControl(name="form.button.Modify").click()

        # Check that user does not exist anymore
        self.browser.getControl(name="searchstring").value = "TWrMCLIo"
        self.browser.getControl(name="form.button.Search").click()
        self.assertNotIn("Autumn Brooks", self.browser.contents)

    def test_groups_search_by_id(self):
        self.browser.open(self.groups_url)
        self.browser.getControl(name="searchstring").value = "group1"
        self.browser.getControl(name="form.button.Search").click()
        self.assertIn("Group 1", self.browser.contents)

    def test_groups_search_by_name(self):
        self.browser.open(self.groups_url)
        self.browser.getControl(name="searchstring").value = "Group 3 accentué"
        self.browser.getControl(name="form.button.Search").click()
        self.assertIn("Group 3 accentué", self.browser.contents)

    def test_groups_modify_roles(self):
        self.browser.open(self.groups_url)
        self.browser.getControl(name="searchstring").value = "group1"

        # Check that role is not selected yet and then select it and apply it.
        form = self.browser.getForm(id="groups_search")
        ctrls = form._form.fields.get("group_group1:list")
        roles = [ctrl._value for ctrl in ctrls]
        expected = "Site Administrator"
        self.assertIn(expected, roles)
        idx = roles.index(expected)
        self.assertFalse(ctrls[idx].checked)
        ctrls[idx].checked = True
        self.browser.getControl("Save").click()

        # Check that role is now selected
        form = self.browser.getForm(id="groups_search")
        ctrl = form._form.get("group_group1:list", index=idx)
        self.assertEqual(ctrl._value, expected)
        self.assertTrue(ctrl.checked)

    def test_groups_delete_group(self):
        self.browser.open(self.groups_url)
        self.browser.getControl(name="searchstring").value = "group1"

        # Delete a group
        self.browser.getControl(name="delete:list").getControl(
            value="group1"
        ).selected = True
        self.browser.getControl(name="form.button.Modify").click()

        # Check that group doesn't exist anymore
        self.browser.getControl(name="searchstring").value = "group1"
        self.assertNotIn("Group 1", self.browser.contents)

    def test_groups_show_all(self):
        self.browser.open(self.groups_url)
        self.browser.getControl(name="form.button.FindAll").click()

        for group in self.groups:
            self.assertIn(group["title"], self.browser.contents)

    def test_group_add_users(self):
        self.browser.open(self.groups_url)
        self.browser.getLink("Group 1 (group1)").click()
        self.assertIn(
            "There is no group or user attached to this group.", self.browser.contents
        )

        # Add user (Autumn Brooks) to selected group (Group 1)
        self.browser.getControl(name="searchstring").value = "TWrMCLIo"
        self.browser.getControl(name="form.button.Search").click()
        self.browser.getControl(name="add:list").getControl(
            value="TWrMCLIo"
        ).selected = True

        # Check that user is now part of the group
        self.browser.getControl("Add selected groups and users to this group").click()
        self.assertIn("Autumn Brooks", self.browser.contents)

    def test_group_add_group(self):
        self.browser.open(self.groups_url)
        self.browser.getLink("Group 1 (group1)").click()
        self.assertIn(
            "There is no group or user attached to this group.", self.browser.contents
        )

        # Add group2 to selected  group 1
        self.browser.getControl(name="searchstring").value = "group2"
        self.browser.getControl(name="form.button.Search").click()
        self.browser.getControl(name="add:list").getControl(
            value="group2"
        ).selected = True

        # Check that group is now part of the group
        self.browser.getControl("Add selected groups and users to this group").click()
        self.assertIn("Group 2", self.browser.contents)

        # Check that you can still add a user too.  This failed at some point:
        # https://github.com/plone/Products.CMFPlone/issues/3048
        # Add user (Autumn Brooks) to selected group (Group 1)
        self.browser.getControl(name="searchstring").value = "TWrMCLIo"
        self.browser.getControl(name="form.button.Search").click()
        self.browser.getControl(name="add:list").getControl(
            value="TWrMCLIo"
        ).selected = True
        self.browser.getControl("Add selected groups and users to this group").click()

        # Check that both group and user are now part of the group
        self.browser.open(self.groups_url)
        self.browser.getLink("Group 1 (group1)").click()
        self.assertIn("Autumn Brooks", self.browser.contents)
        self.assertIn("Group 2", self.browser.contents)

    def test_usergroups_settings_many_users(self):
        self.browser.open("%s/@@usergroup-controlpanel" % self.portal_url)
        self.browser.getControl(name="form.widgets.many_users:list").controls[
            0
        ].selected = True
        self.browser.getControl("Save").click()

        # Check that show all button for users is no longer available
        self.browser.open(self.users_url)
        self.assertNotIn("Show all", self.browser.contents)

        # Check that empty search does not trigger show all
        self.browser.open(self.users_url)
        self.browser.getControl(name="searchstring").value = ""

    def test_usergroups_settings_many_groups(self):
        self.browser.open("%s/@@usergroup-controlpanel" % self.portal_url)
        self.browser.getControl(name="form.widgets.many_groups:list").controls[
            0
        ].selected = True
        self.browser.getControl("Save").click()

        # Check that show all button for groups is no longer available
        self.browser.open(self.groups_url)
        self.assertNotIn("Show all", self.browser.contents)
        self.assertNotIn("DIispfuF", self.browser.contents)

    def test_usergroups_membership_many_users(self):
        from io import StringIO
        from lxml import etree

        # add user | many_users=False | many_groups=False
        self.browser.open(
            "%s/@@usergroup-groupmembership?groupname=group1" % self.portal_url
        )
        self.browser.getControl(name="searchstring").value = "TWrMCLIo"
        self.browser.getControl(name="form.button.Search").click()
        self.browser.getControl(name="add:list").getControl(
            value="TWrMCLIo"
        ).selected = True
        self.browser.getControl("Add selected groups and users to this group").click()

        tree = etree.parse(StringIO(self.browser.contents), etree.HTMLParser())
        result = tree.xpath("count(//table[@summary='Groups']/tbody/tr)")

        # Rows with User Entries exists
        self.assertGreater(result, 1.0, "Table should contain User Entries")

        # delete the user
        self.browser.open(
            "%s/@@usergroup-groupmembership?groupname=group1" % self.portal_url
        )
        self.browser.getControl(name="searchstring").value = "TWrMCLIo"
        self.browser.getControl(name="form.button.Search").click()
        self.browser.getControl(name="delete:list").getControl(
            value="TWrMCLIo"
        ).selected = True
        self.browser.getControl("Remove selected groups / users").click()

        # set many_user and many_groups to True
        self.browser.open("%s/@@usergroup-controlpanel" % self.portal_url)

        self.browser.getControl(name="form.widgets.many_users:list").controls[
            0
        ].selected = True
        self.browser.getControl(name="form.widgets.many_groups:list").controls[
            0
        ].selected = True
        self.browser.getControl("Save").click()

        # add user | many_users=True | many_groups=True
        self.browser.open(
            "%s/@@usergroup-groupmembership?groupname=group1" % self.portal_url
        )
        self.browser.getControl(name="searchstring").value = "j5g0xPmr"
        self.browser.getControl(name="form.button.Search").click()
        self.browser.getControl(name="add:list").getControl(
            value="j5g0xPmr"
        ).selected = True
        self.browser.getControl("Add selected groups and users to this group").click()

        tree = etree.parse(StringIO(self.browser.contents), etree.HTMLParser())
        result = tree.xpath("count(//table[@summary='Groups']/tbody/tr)")

        # No Rows with User Entries exists, only a row with a hint-text is visible
        self.assertEqual(1.0, result, "Table should contain no User Entries")
