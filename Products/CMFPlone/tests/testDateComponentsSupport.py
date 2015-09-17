from plone.app.testing.bbb import PloneTestCase

from DateTime import DateTime


def sortTuple(t):
    l = list(t)
    l.sort()
    return tuple(l)


class TestDateComponentsSupport(PloneTestCase):

    def afterSetUp(self):
        date = DateTime(2002, 8, 1, 17, 42, 0)
        self.d = self.portal.date_components_support(date)

    def testElements(self):
        self.assertEqual(sortTuple(self.d.keys()),
                ('ampm', 'days', 'hours', 'minutes', 'months', 'years'))

    def testYears(self):
        this_year = DateTime().year()
        from plone.registry.interfaces import IRegistry
        from zope.component import getUtility
        registry = getUtility(IRegistry)
        min_year = registry.get('Products.Archetypes.calendar_starting_year', 1999)
        max_year = registry.get('Products.Archetypes.calendar_future_years_available', 5) + this_year

        data = [
            {'selected': None, 'id': '--', 'value': '0000'}
        ]

        for y in range(min_year, max_year + 1):
            d = {'selected': None, 'id': y, 'value': y}
            if y == 2002:
                d['selected'] = 1
            data.append(d)

        years = self.d.get('years')
        for i in range(max_year - min_year + 1):
            self.assertEqual(years[i], data[i])

    def testMonths(self):
        data = [
            {'selected': None, 'id': '--',        'value': '00'},
            {'selected': None, 'id': 'January',   'value': '01'},
            {'selected': None, 'id': 'February',  'value': '02'},
            {'selected': None, 'id': 'March',     'value': '03'},
            {'selected': None, 'id': 'April',     'value': '04'},
            {'selected': None, 'id': 'May',       'value': '05'},
            {'selected': None, 'id': 'June',      'value': '06'},
            {'selected': None, 'id': 'July',      'value': '07'},
            {'selected': 1,    'id': 'August',    'value': '08'},
            {'selected': None, 'id': 'September', 'value': '09'},
            {'selected': None, 'id': 'October',   'value': '10'},
            {'selected': None, 'id': 'November',  'value': '11'},
            {'selected': None, 'id': 'December',  'value': '12'},
        ]

        months = self.d.get('months')
        for i in range(13):
            self.assertEqual(months[i], data[i])

    def testDays(self):
        data = [
            {'selected': None, 'id': '--',   'value': '00'},
            {'selected': 1,    'id': 1,      'value': '01'},
            {'selected': None, 'id': 2,      'value': '02'},
            {'selected': None, 'id': 3,      'value': '03'},
            {'selected': None, 'id': 4,      'value': '04'},
            {'selected': None, 'id': 5,      'value': '05'},
            {'selected': None, 'id': 6,      'value': '06'},
            {'selected': None, 'id': 7,      'value': '07'},
            {'selected': None, 'id': 8,      'value': '08'},
            {'selected': None, 'id': 9,      'value': '09'},
            {'selected': None, 'id': 10,     'value': '10'},
            {'selected': None, 'id': 11,     'value': '11'},
            {'selected': None, 'id': 12,     'value': '12'},
            {'selected': None, 'id': 13,     'value': '13'},
            {'selected': None, 'id': 14,     'value': '14'},
            {'selected': None, 'id': 15,     'value': '15'},
            {'selected': None, 'id': 16,     'value': '16'},
            {'selected': None, 'id': 17,     'value': '17'},
            {'selected': None, 'id': 18,     'value': '18'},
            {'selected': None, 'id': 19,     'value': '19'},
            {'selected': None, 'id': 20,     'value': '20'},
            {'selected': None, 'id': 21,     'value': '21'},
            {'selected': None, 'id': 22,     'value': '22'},
            {'selected': None, 'id': 23,     'value': '23'},
            {'selected': None, 'id': 24,     'value': '24'},
            {'selected': None, 'id': 25,     'value': '25'},
            {'selected': None, 'id': 26,     'value': '26'},
            {'selected': None, 'id': 27,     'value': '27'},
            {'selected': None, 'id': 28,     'value': '28'},
            {'selected': None, 'id': 29,     'value': '29'},
            {'selected': None, 'id': 30,     'value': '30'},
            {'selected': None, 'id': 31,     'value': '31'},
        ]

        days = self.d.get('days')
        for i in range(32):
            self.assertEqual(days[i], data[i])

    def testHours(self):
        data = [
            {'selected': None, 'id': '--',   'value': '00'},
            {'selected': None, 'id': '00',   'value': '00'},
            {'selected': None, 'id': '01',   'value': '01'},
            {'selected': None, 'id': '02',   'value': '02'},
            {'selected': None, 'id': '03',   'value': '03'},
            {'selected': None, 'id': '04',   'value': '04'},
            {'selected': None, 'id': '05',   'value': '05'},
            {'selected': None, 'id': '06',   'value': '06'},
            {'selected': None, 'id': '07',   'value': '07'},
            {'selected': None, 'id': '08',   'value': '08'},
            {'selected': None, 'id': '09',   'value': '09'},
            {'selected': None, 'id': '10',   'value': '10'},
            {'selected': None, 'id': '11',   'value': '11'},
            {'selected': None, 'id': '12',   'value': '12'},
            {'selected': None, 'id': '13',   'value': '13'},
            {'selected': None, 'id': '14',   'value': '14'},
            {'selected': None, 'id': '15',   'value': '15'},
            {'selected': None, 'id': '16',   'value': '16'},
            {'selected': 1,    'id': '17',   'value': '17'},
            {'selected': None, 'id': '18',   'value': '18'},
            {'selected': None, 'id': '19',   'value': '19'},
            {'selected': None, 'id': '20',   'value': '20'},
            {'selected': None, 'id': '21',   'value': '21'},
            {'selected': None, 'id': '22',   'value': '22'},
            {'selected': None, 'id': '23',   'value': '23'},
        ]

        hours = self.d.get('hours')
        for i in range(25):
            self.assertEqual(hours[i], data[i])

    def testMinutes(self):
        data = [
            {'selected': None, 'id': '--',   'value': '00'},
            {'selected': None, 'id': '00',   'value': '00'},
            {'selected': None, 'id': '05',   'value': '05'},
            {'selected': None, 'id': '10',   'value': '10'},
            {'selected': None, 'id': '15',   'value': '15'},
            {'selected': None, 'id': '20',   'value': '20'},
            {'selected': None, 'id': '25',   'value': '25'},
            {'selected': None, 'id': '30',   'value': '30'},
            {'selected': None, 'id': '35',   'value': '35'},
            {'selected': None, 'id': '40',   'value': '40'},
            {'selected': 1,    'id': '45',   'value': '45'},
            {'selected': None, 'id': '50',   'value': '50'},
            {'selected': None, 'id': '55',   'value': '55'},
        ]

        minutes = self.d.get('minutes')
        for i in range(13):
            self.assertEqual(minutes[i], data[i])

    def testAM(self):
        d = DateTime(2002, 8, 1, 3, 0, 0)
        d = self.portal.date_components_support(d)
        self.assertEqual(d.get('ampm'), [])

    def testPM(self):
        ampm = self.d.get('ampm')
        self.assertEqual(ampm, [])


class TestDateComponentsSupportDefault(PloneTestCase):

    def afterSetUp(self):
        self.d = self.portal.date_components_support(None)

    def testElements(self):
        self.assertEqual(sortTuple(self.d.keys()),
                ('ampm', 'days', 'hours', 'minutes', 'months', 'years'))

    def testYears(self):
        this_year = DateTime().year()
        from plone.registry.interfaces import IRegistry
        from zope.component import getUtility
        registry = getUtility(IRegistry)
        min_year = registry.get('Products.Archetypes.calendar_starting_year', 1999)
        max_year = registry.get('Products.Archetypes.calendar_future_years_available', 5) + this_year

        data = [
            {'selected': None, 'id': '--', 'value': '0000'}
        ]

        for y in range(min_year, max_year + 1):
            d = {'selected': None, 'id': y, 'value': y}
            if y == this_year:
                d['selected'] = 1
            data.append(d)

        years = self.d.get('years')
        for i in range(max_year - min_year + 1):
            self.assertEqual(years[i], data[i])

    def testMonths(self):
        data = [
            {'selected': 1,    'id': '--',        'value': '00'},
            {'selected': None, 'id': 'January',   'value': '01'},
            {'selected': None, 'id': 'February',  'value': '02'},
            {'selected': None, 'id': 'March',     'value': '03'},
            {'selected': None, 'id': 'April',     'value': '04'},
            {'selected': None, 'id': 'May',       'value': '05'},
            {'selected': None, 'id': 'June',      'value': '06'},
            {'selected': None, 'id': 'July',      'value': '07'},
            {'selected': None, 'id': 'August',    'value': '08'},
            {'selected': None, 'id': 'September', 'value': '09'},
            {'selected': None, 'id': 'October',   'value': '10'},
            {'selected': None, 'id': 'November',  'value': '11'},
            {'selected': None, 'id': 'December',  'value': '12'},
        ]

        months = self.d.get('months')
        for i in range(13):
            self.assertEqual(months[i], data[i])

    def testDays(self):
        data = [
            {'selected': 1,    'id': '--',   'value': '00'},
            {'selected': None, 'id': 1,      'value': '01'},
            {'selected': None, 'id': 2,      'value': '02'},
            {'selected': None, 'id': 3,      'value': '03'},
            {'selected': None, 'id': 4,      'value': '04'},
            {'selected': None, 'id': 5,      'value': '05'},
            {'selected': None, 'id': 6,      'value': '06'},
            {'selected': None, 'id': 7,      'value': '07'},
            {'selected': None, 'id': 8,      'value': '08'},
            {'selected': None, 'id': 9,      'value': '09'},
            {'selected': None, 'id': 10,     'value': '10'},
            {'selected': None, 'id': 11,     'value': '11'},
            {'selected': None, 'id': 12,     'value': '12'},
            {'selected': None, 'id': 13,     'value': '13'},
            {'selected': None, 'id': 14,     'value': '14'},
            {'selected': None, 'id': 15,     'value': '15'},
            {'selected': None, 'id': 16,     'value': '16'},
            {'selected': None, 'id': 17,     'value': '17'},
            {'selected': None, 'id': 18,     'value': '18'},
            {'selected': None, 'id': 19,     'value': '19'},
            {'selected': None, 'id': 20,     'value': '20'},
            {'selected': None, 'id': 21,     'value': '21'},
            {'selected': None, 'id': 22,     'value': '22'},
            {'selected': None, 'id': 23,     'value': '23'},
            {'selected': None, 'id': 24,     'value': '24'},
            {'selected': None, 'id': 25,     'value': '25'},
            {'selected': None, 'id': 26,     'value': '26'},
            {'selected': None, 'id': 27,     'value': '27'},
            {'selected': None, 'id': 28,     'value': '28'},
            {'selected': None, 'id': 29,     'value': '29'},
            {'selected': None, 'id': 30,     'value': '30'},
            {'selected': None, 'id': 31,     'value': '31'},
        ]

        days = self.d.get('days')
        for i in range(32):
            self.assertEqual(days[i], data[i])

    def testHours(self):
        data = [
            {'selected': 1,    'id': '--',   'value': '00'},
            {'selected': None, 'id': '00',   'value': '00'},
            {'selected': None, 'id': '01',   'value': '01'},
            {'selected': None, 'id': '02',   'value': '02'},
            {'selected': None, 'id': '03',   'value': '03'},
            {'selected': None, 'id': '04',   'value': '04'},
            {'selected': None, 'id': '05',   'value': '05'},
            {'selected': None, 'id': '06',   'value': '06'},
            {'selected': None, 'id': '07',   'value': '07'},
            {'selected': None, 'id': '08',   'value': '08'},
            {'selected': None, 'id': '09',   'value': '09'},
            {'selected': None, 'id': '10',   'value': '10'},
            {'selected': None, 'id': '11',   'value': '11'},
            {'selected': None, 'id': '12',   'value': '12'},
            {'selected': None, 'id': '13',   'value': '13'},
            {'selected': None, 'id': '14',   'value': '14'},
            {'selected': None, 'id': '15',   'value': '15'},
            {'selected': None, 'id': '16',   'value': '16'},
            {'selected': None, 'id': '17',   'value': '17'},
            {'selected': None, 'id': '18',   'value': '18'},
            {'selected': None, 'id': '19',   'value': '19'},
            {'selected': None, 'id': '20',   'value': '20'},
            {'selected': None, 'id': '21',   'value': '21'},
            {'selected': None, 'id': '22',   'value': '22'},
            {'selected': None, 'id': '23',   'value': '23'},
        ]

        hours = self.d.get('hours')
        for i in range(25):
            self.assertEqual(hours[i], data[i])

    def testMinutes(self):
        data = [
            {'selected': 1,    'id': '--',   'value': '00'},
            {'selected': None, 'id': '00',   'value': '00'},
            {'selected': None, 'id': '05',   'value': '05'},
            {'selected': None, 'id': '10',   'value': '10'},
            {'selected': None, 'id': '15',   'value': '15'},
            {'selected': None, 'id': '20',   'value': '20'},
            {'selected': None, 'id': '25',   'value': '25'},
            {'selected': None, 'id': '30',   'value': '30'},
            {'selected': None, 'id': '35',   'value': '35'},
            {'selected': None, 'id': '40',   'value': '40'},
            {'selected': None, 'id': '45',   'value': '45'},
            {'selected': None, 'id': '50',   'value': '50'},
            {'selected': None, 'id': '55',   'value': '55'},
        ]

        minutes = self.d.get('minutes')
        for i in range(13):
            self.assertEqual(minutes[i], data[i])

    def testAMPM(self):
        ampm = self.d.get('ampm')
        self.assertEqual(ampm, [])


class TestDateComponentsSupportAMPM(PloneTestCase):

    def afterSetUp(self):
        date = DateTime(2002, 8, 1, 17, 42, 0)
        self.d = self.portal.date_components_support(date, use_ampm=1)

    def testElements(self):
        self.assertEqual(sortTuple(self.d.keys()),
                ('ampm', 'days', 'hours', 'minutes', 'months', 'years'))

    def testHours(self):
        data = [
            {'selected': None, 'id': '--',   'value': '12'},
            {'selected': None, 'id': '12',   'value': '12'},
            {'selected': None, 'id': '01',   'value': '01'},
            {'selected': None, 'id': '02',   'value': '02'},
            {'selected': None, 'id': '03',   'value': '03'},
            {'selected': None, 'id': '04',   'value': '04'},
            {'selected': 1,    'id': '05',   'value': '05'},
            {'selected': None, 'id': '06',   'value': '06'},
            {'selected': None, 'id': '07',   'value': '07'},
            {'selected': None, 'id': '08',   'value': '08'},
            {'selected': None, 'id': '09',   'value': '09'},
            {'selected': None, 'id': '10',   'value': '10'},
            {'selected': None, 'id': '11',   'value': '11'},
        ]

        hours = self.d.get('hours')
        for i in range(13):
            self.assertEqual(hours[i], data[i])

    def testAM(self):
        d = DateTime(2002, 8, 1, 3, 0, 0)
        d = self.portal.date_components_support(d, use_ampm=1)

        data = [
            {'selected': None, 'id': '--',   'value': 'AM'},
            {'selected': 1,    'id': 'AM',   'value': 'AM'},
            {'selected': None, 'id': 'PM',   'value': 'PM'},
        ]

        ampm = d.get('ampm')
        for i in range(3):
            self.assertEqual(ampm[i], data[i])

    def testPM(self):
        data = [
            {'selected': None, 'id': '--',   'value': 'AM'},
            {'selected': None, 'id': 'AM',   'value': 'AM'},
            {'selected': 1,    'id': 'PM',   'value': 'PM'},
        ]

        ampm = self.d.get('ampm')
        for i in range(3):
            self.assertEqual(ampm[i], data[i])


class TestDateComponentsSupportAMPMDefault(PloneTestCase):

    def afterSetUp(self):
        self.d = self.portal.date_components_support(None, use_ampm=1)

    def testElements(self):
        self.assertEqual(sortTuple(self.d.keys()),
                ('ampm', 'days', 'hours', 'minutes', 'months', 'years'))

    def testHours(self):
        data = [
            {'selected': 1,    'id': '--',   'value': '12'},
            {'selected': None, 'id': '12',   'value': '12'},
            {'selected': None, 'id': '01',   'value': '01'},
            {'selected': None, 'id': '02',   'value': '02'},
            {'selected': None, 'id': '03',   'value': '03'},
            {'selected': None, 'id': '04',   'value': '04'},
            {'selected': None, 'id': '05',   'value': '05'},
            {'selected': None, 'id': '06',   'value': '06'},
            {'selected': None, 'id': '07',   'value': '07'},
            {'selected': None, 'id': '08',   'value': '08'},
            {'selected': None, 'id': '09',   'value': '09'},
            {'selected': None, 'id': '10',   'value': '10'},
            {'selected': None, 'id': '11',   'value': '11'},
        ]

        hours = self.d.get('hours')
        for i in range(13):
            self.assertEqual(hours[i], data[i])

    def testAMPM(self):
        data = [
            {'selected': 1,    'id': '--', 'value': 'AM'},
            {'selected': None, 'id': 'AM',   'value': 'AM'},
            {'selected': None, 'id': 'PM',   'value': 'PM'},
        ]

        ampm = self.d.get('ampm')
        for i in range(2):
            self.assertEqual(ampm[i], data[i])


class TestDateComponentsSupportMinuteStepDefault(PloneTestCase):

    def testMinutesStep1(self):
        data = [
            {'selected': 1,    'id': '--', 'value': '00'},
        ]
        for x in range(0, 60, 1):
            d = {'id': '%02d' % x, 'value': '%02d' % x, 'selected': None}
            data.append(d)

        d = self.portal.date_components_support(None, minute_step=1)
        minutes = d.get('minutes')
        for i in range(61):
            self.assertEqual(minutes[i], data[i])

    def testMinutesStep10(self):
        data = [
            {'selected': 1,    'id': '--', 'value': '00'},
        ]
        for x in range(0, 60, 10):
            d = {'id': '%02d' % x, 'value': '%02d' % x, 'selected': None}
            data.append(d)

        d = self.portal.date_components_support(None, minute_step=10)
        minutes = d.get('minutes')
        for i in range(7):
            self.assertEqual(minutes[i], data[i])


class TestSpecialCases(PloneTestCase):

    def testNoneUsesDefault(self):
        d = self.portal.date_components_support(None)
        hours = d.get('hours')
        # default == 1
        self.assertTrue(hours[0]['selected'])

    def testEmptyStringUsesDefault(self):
        d = self.portal.date_components_support('')
        hours = d.get('hours')
        # default == 1
        self.assertTrue(hours[0]['selected'])

    def testDateWithGMT(self):
        # Any GMT suffix gets truncated
        d = self.portal.date_components_support('2004/08/31 04:30:00 GMT+2')
        hours = d.get('hours')
        # default == 0
        self.assertTrue(hours[5]['selected'])   # 4th hour

    def testDateOnly(self):
        d = self.portal.date_components_support('2004/08/31')
        hours = d.get('hours')
        # default == 0
        self.assertTrue(hours[1]['selected'])   # 0th hour

    def testInvalidDateWithGMT(self):
        # Any GMT suffix gets truncated
        d = self.portal.date_components_support('2004/02/31 00:30:00 GMT+2')
        hours = d.get('hours')
        # default == 1
        self.assertTrue(hours[0]['selected'])

    def testInvalidDateOnly(self):
        d = self.portal.date_components_support('2004/02/31')
        hours = d.get('hours')
        # default == 1
        self.assertTrue(hours[0]['selected'])
