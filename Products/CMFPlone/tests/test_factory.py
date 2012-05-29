# -*- coding: utf-8 -*-
from Products.CMFPlone.tests import PloneTestCase
from Products.CMFPlone.factory import addPloneSite


class TestFactoryPloneSite(PloneTestCase.PloneTestCase):

    def testPlonesiteWithUnicodeTitle(self):
        TITLE = 'Ploné'
        ploneSite = addPloneSite(self.app, 'ploneFoo', title=TITLE,
                     setup_content=False)
        ploneSiteTitleProperty = ploneSite.getProperty('title')
        # CMF stores title as string only so Plone should keep the same track
        self.assertTrue(isinstance(ploneSiteTitleProperty, str))
        self.assertEqual(ploneSiteTitleProperty, TITLE)
        ploneSiteTitle = ploneSite.Title()
        self.assertTrue(isinstance(ploneSiteTitle, str))
        self.assertEqual(ploneSiteTitle, TITLE)

    def testPlonesiteWithoutUnicodeTitle(self):
        TITLE = 'Plone'
        ploneSite = addPloneSite(self.app, 'ploneFoo', title=TITLE,
                     setup_content=False)
        ploneSiteTitleProperty = ploneSite.getProperty('title')
        # CMF stores title as string only so Plone should keep the same track
        self.assertTrue(isinstance(ploneSiteTitleProperty, str))
        self.assertEqual(ploneSiteTitleProperty, TITLE)
        ploneSiteTitle = ploneSite.Title()
        self.assertTrue(isinstance(ploneSiteTitle, str))
        self.assertEqual(ploneSiteTitle, TITLE)
