from plone.app.testing.bbb import PloneTestCase
from Products.CMFPlone.interfaces.controlpanel import IImagingSchema
from plone.registry.interfaces import IRegistry
from zope.component import getUtility


class TestImagingSchemaTool(PloneTestCase):

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
