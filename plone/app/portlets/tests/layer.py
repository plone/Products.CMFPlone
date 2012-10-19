from Products.PloneTestCase.layer import PloneSite
from Testing.ZopeTestCase import installPackage

try:
    from Zope2.App import zcml
    from OFS import metaconfigure
    zcml # pyflakes
    metaconfigure
except ImportError:
    from Products.Five import zcml
    from Products.Five import fiveconfigure as metaconfigure


class PlonePortlets(PloneSite):

    @classmethod
    def setUp(cls):
        metaconfigure.debug_mode = True
        import plone.app.portlets
        zcml.load_config('configure.zcml', plone.app.portlets)
        metaconfigure.debug_mode = False
        installPackage('plone.app.portlets', quiet=True)

    @classmethod
    def tearDown(cls):
        pass
