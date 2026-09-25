from Products.CMFPlone.testing import PRODUCTS_CMFPLONE_INTEGRATION_TESTING
from zope.i18nmessageid import Message

import unittest


class TestControlPanel(unittest.TestCase):
    layer = PRODUCTS_CMFPLONE_INTEGRATION_TESTING

    def setUp(self):
        self.controlpanel = self.layer["portal"].portal_controlpanel

        # get the expected default groups and configlets
        self.groups = ["Plone", "Products"]
        self.configlets = [
            "QuickInstaller",
            "MailHost",
            "UsersGroups",
            "PortalSkin",
            "ZMI",
            "SecuritySettings",
            "NavigationSettings",
            "SearchSettings",
            "errorLog",
            "PloneReconfig",
            "TypesSettings",
            "FilterSettings",
            "Maintenance",
        ]

    def testDefaultGroups(self):
        for group in self.groups:
            self.assertTrue(
                group in self.controlpanel.getGroupIds(),
                "Missing group with id '%s'" % group,
            )

    def testDefaultConfiglets(self):
        for title in self.configlets:
            self.assertTrue(
                title
                in [a.getAction(self)["id"] for a in self.controlpanel.listActions()],
                "Missing configlet with id '%s'" % title,
            )

    def _add_configlet(self):
        self.controlpanel.addAction(
            id="my-configlet",
            name=Message("My Configlet", domain="test.domain"),
            action="",
            permission="",
            category="Plone",
        )
        return len(self.controlpanel.listActions()) - 1

    def _form_properties(self):
        """Builds the form data the way manage_editActionsForm does.

        The title (name) is the stringified current title.
        """
        properties = {}
        for i, a in enumerate(self.controlpanel.listActions()):
            properties["id_%d" % i] = a.getId()
            properties["name_%d" % i] = str(a.Title())
        return properties

    def testChangeActionsPreservesI18nTitle(self):
        """The submitted title is a plain string, not a Message."""
        index = self._add_configlet()
        properties = self._form_properties()
        self.assertNotIsInstance(properties["name_%d" % index], Message)

        self.controlpanel.changeActions(properties=properties)

        new_action = self.controlpanel.listActions()[index]
        self.assertIsInstance(new_action.title, Message)
        self.assertEqual(new_action.title.domain, "test.domain")

    def testChangeActionsAllowsTitleChange(self):
        """Manual changes to the title should be applied."""
        index = self._add_configlet()
        properties = self._form_properties()
        properties[f"name_{index}"] = "Renamed Configlet"

        self.controlpanel.changeActions(properties=properties)

        new_action = self.controlpanel.listActions()[index]
        self.assertEqual(new_action.title, "Renamed Configlet")
        self.assertNotIsInstance(new_action.title, Message)

    def testExtractActionMatchesOldTitleById(self):
        """A stale form may submit the rows with different indexes."""
        index = self._add_configlet()
        stale_index = index + 1
        properties = {
            f"id_{stale_index}": "my-configlet",
            f"name_{stale_index}": "My Configlet",
        }

        action = self.controlpanel._extractAction(properties, stale_index)

        self.assertIsInstance(action.title, Message)
        self.assertEqual(action.title.domain, "test.domain")

    def testExtractActionWithUnknownIdDoesNotFail(self):
        """A stale form may reference a configlet that no longer exists."""
        properties = {
            "id_0": "removed-configlet",
            "name_0": "Removed Configlet",
        }

        action = self.controlpanel._extractAction(properties, 0)

        self.assertEqual(action.title, "Removed Configlet")
        self.assertNotIsInstance(action.title, Message)
