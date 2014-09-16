import zope.interface
import zope.component
from zope import schema
from Products.CMFPlone import PloneMessageFactory as _


class IPatternConfiguration(zope.interface.Interface):

    configuration = schema.Text(
        title=_(u"JSON configuration"),
        default=u'{}',
        required=True)
