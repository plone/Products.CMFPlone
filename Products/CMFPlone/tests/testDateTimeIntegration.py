# tests for issues related to changes in `DateTime` 2.12
# please see tickets:
#
#   http://dev.plone.org/plone/ticket/10140
#   http://dev.plone.org/plone/ticket/10141
#   http://dev.plone.org/plone/ticket/10171
#
# for more information about this.  please also note that these tests
# may produce false positives when run in the GMT time zone!

from Products.CMFPlone.tests.PloneTestCase import PloneTestCase
from DateTime import DateTime
from time import localtime


class DateTimeTests(PloneTestCase):

    def testModificationDate(self):
        obj = self.folder
        before = DateTime()
        obj.processForm(values=dict(Description='foo!'))
        after = DateTime()
        modified = obj.ModificationDate()   # the string representation...
        modified = DateTime(modified)       # is usually parsed again in Plone
        self.assertTrue(int(before) <= int(modified) <= int(after),
            (before, modified, after))

    def testCreationDate(self):
        before = DateTime()
        obj = self.folder[self.folder.invokeFactory('Document', 'foo')]
        after = DateTime()
        creation = obj.CreationDate()       # the string representation...
        creation = DateTime(creation)       # is usually parsed again in Plone
        self.assertTrue(int(before) <= int(creation) <= int(after),
            (before, creation, after))

    def testEffectiveDate(self):
        obj = self.folder
        date = DateTime() + 365             # expire one year from today
        date = DateTime(date.ISO8601())     # but strip off milliseconds
        obj.setEffectiveDate(date)
        obj.processForm(values=dict(Description='foo!'))
        effective = obj.EffectiveDate()     # the string representation...
        effective = DateTime(effective)     # is usually parsed again in Plone
        self.assertTrue(date.equalTo(effective), (date, effective))

    def testExpirationDate(self):
        obj = self.folder
        date = DateTime() + 365             # expire one year from today
        date = DateTime(date.ISO8601())     # but strip off milliseconds
        obj.setExpirationDate(date)
        obj.processForm(values=dict(Description='foo!'))
        expired = obj.ExpirationDate()      # the string representation...
        expired = DateTime(expired)         # is usually parsed again in Plone
        self.assertTrue(date.equalTo(expired), (date, expired))
