""" Unit tests for Products.CMFPlone.i18nl10n module. """

import unittest

class BasicI18nl10nTests(unittest.TestCase):

    def test_regexp_dt_format_string_regexp(self):
        from Products.CMFPlone.i18nl10n import _dt_format_string_regexp
        dt_string = "%Y-%m-%d %H:%M"
        locales_string = "${H}:${M}"

        # test for strftime format string
        self.assertTrue(bool(_dt_format_string_regexp.findall(dt_string)))
        self.assertFalse(bool(_dt_format_string_regexp.findall(locales_string)))

    def test_regexp_interp_regex(self):
        from Products.CMFPlone.i18nl10n import _interp_regex
        locales_string = "${H}:${M}"

        # test for locale string elements:
        self.assertEquals(
            _interp_regex.findall(locales_string),
            ["${H}", "${M}"],
        )
