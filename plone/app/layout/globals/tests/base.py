from Products.PloneTestCase import PloneTestCase
PloneTestCase.setupPloneSite()


class GlobalsTestCase(PloneTestCase.PloneTestCase):
    pass


class GlobalsFunctionalTestCase(PloneTestCase.FunctionalTestCase):
    pass
