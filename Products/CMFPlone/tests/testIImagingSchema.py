# -*- coding: utf-8 -*-
from plone.app.testing import PLONE_INTEGRATION_TESTING
from plone.registry.interfaces import IRegistry
from Products.CMFPlone.interfaces.controlpanel import IImagingSchema
from zope.component import getUtility

import unittest


class TestImagingSchemaTool(unittest.TestCase):

    layer = PLONE_INTEGRATION_TESTING

    def test_AllowedSizes(self):
        registry = getUtility(IRegistry)
        imaging_settings = registry.forInterface(IImagingSchema, prefix='plone')

        # Ensure we can save the defaults back to the registry
        imaging_settings.allowed_sizes = imaging_settings.allowed_sizes

        # Add a new image scale
        sizes = imaging_settings.allowed_sizes
        imaging_settings.allowed_sizes = sizes + [u"larger 800:800"]

        # Set back to original
        imaging_settings.allowed_sizes = sizes
