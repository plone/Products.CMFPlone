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
from Products.CMFPlone.tests.PloneTestCase import FunctionalTestCase
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


class DateTimeFunctionalTests(FunctionalTestCase):

    def testNonDSTPublicationDateRemainsUnchangedThroughEdit(self):
        # this test is for a date when daylight savings time is not in effect
        self.setRoles(('Manager',))
        obj = self.portal['front-page']
        # the test is performed in the local timezone, and in 2 two alternate
        # timezones (to make sure one is different from the local timezone)
        for tz in ('', ' US/Central', ' US/Eastern'):
            # save the time represented in the specified time zone
            obj.setEffectiveDate('2020-02-20 00:00%s' % tz)
            self.assertTrue(obj.effective_date.ISO8601().startswith(
                '2020-02-20T00:00:00'))
            start_value = obj.effective_date
            browser = self.getBrowser()
            browser.open(obj.absolute_url())
            browser.getLink('Edit').click()
            # Time should appear on the edit page in the timezone that was
            # local for that date (not always the same, due to DST)
            local_zone = start_value.localZone(
                            localtime(start_value.timeTime()))
            local_start_value = start_value.toZone(local_zone)
            localHour = local_start_value.h_12()
            localAMPM = local_start_value.ampm().upper()
            self.assertEqual(
                   localHour,
                   int(browser.getControl(name='effectiveDate_hour').value[0]))
            self.assertEqual(
                           [localAMPM],
                           browser.getControl(name='effectiveDate_ampm').value)
            if not tz:
                self.assertEqual(12, localHour)
            browser.getControl('Save').click()
            # Time is saved in the local timezone for the given date
            self.assertEqual(local_start_value.tzoffset(),
                             obj.effective_date.tzoffset())
            # but should be equivalent to the original time
            self.assertTrue(start_value.equalTo(obj.effective_date))

    def testDSTPublicationDateRemainsUnchangedThroughEdit(self):
        # this test is for a date when daylight savings time is in effect
        self.setRoles(('Manager',))
        obj = self.portal['front-page']
        # the test is performed in the local timezone, and in 2 two alternate
        # timezones (to make sure one is different from the local timezone)
        for tz in ('', ' GMT-6', ' GMT-5'):
            # save the time represented in the specified time zone
            obj.setEffectiveDate('2020-06-20 16:00%s' % tz)
            self.assertTrue(obj.effective_date.ISO8601().startswith(
                '2020-06-20T16:00:00'))
            start_value = obj.effective_date
            browser = self.getBrowser()
            browser.open(obj.absolute_url())
            browser.getLink('Edit').click()
            # Time should appear on the edit page in the timezone that was
            # local for that date (not always the same, due to DST)
            local_zone = start_value.localZone(
                            localtime(start_value.timeTime()))
            local_start_value = start_value.toZone(local_zone)
            localHour = local_start_value.h_12()
            localAMPM = local_start_value.ampm().upper()
            self.assertEqual(
                   localHour,
                   int(browser.getControl(name='effectiveDate_hour').value[0]))
            self.assertEqual(
                   [localAMPM],
                   browser.getControl(name='effectiveDate_ampm').value)
            if not tz:
                self.assertEqual(4, localHour)
            browser.getControl('Save').click()
            # Time is saved in the local timezone for the given date
            self.assertEqual(local_start_value.tzoffset(),
                             obj.effective_date.tzoffset())
            # but should be equivalent to the original time
            self.assertTrue(start_value.equalTo(obj.effective_date))

    def testRespectDaylightSavingTime(self):
        """ When saving dates, the date's timezone and Daylight Saving Time
            has to be respected.
            See Products.Archetypes.Field.DateTimeField.set
        """
        self.setRoles(('Manager',))
        obj = self.portal['front-page']
        obj.setEffectiveDate('2010-01-01 10:00 Europe/Belgrade')
        obj.setExpirationDate('2010-06-01 10:00 Europe/Belgrade')
        self.assertTrue(obj.effective_date.tzoffset() == 3600)
        self.assertTrue(obj.expiration_date.tzoffset() == 7200)
