import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase

import zope.app.i18n
from zope.app.tests.placelesssetup import setUp, tearDown
from zope.i18nmessageid import MessageIDFactory
from Products.Five import zcml
from Products.PageTemplates import GlobalTranslationService as GTS

class Z3I18NCornerTestCase(ZopeTestCase.ZopeTestCase):

    def setUp(self):
        self.TS = GTS.getGlobalTranslationService()
        setUp()
        zcml.load_config('meta.zcml', zope.app.i18n)
        configure_zcml = '''
        <configure xmlns="http://namespaces.zope.org/zope"
                   xmlns:i18n="http://namespaces.zope.org/i18n"
                   package="Products.CMFPlone.tests">
          <i18n:registerTranslations directory="locales" />
        </configure>'''
        zcml.load_string(configure_zcml)

    def test_locale_dir(self):
        translated = self.TS.translate('testing', u'testid1', target_language='de')
        self.assertEquals(u'testvalue1', translated,
                          'translation is not working. Got: %s' % translated)
        translated = self.TS.translate('testing', u'testid2', target_language='de')
        self.assertEquals(u'testvalue2', translated,
                          'translation is not working. Got: %s' % translated)
        translated = self.TS.translate('testing', u'testid ${foo}',
                                       target_language='de', mapping={u'foo' : u'value'})
        self.assertEquals(u'testvalue value', translated,
                          'translation is not working. Got: %s' % translated)

    def test_message_id(self):
        _ = MessageIDFactory('testing')
        msg = _(u'explicit-msg', u'This is an explicit message')
        self.assertEquals(u'This is an explicit message',
                          self.TS.translate('testing', msg),
                          'Basic MessageID translation is not working')

    def test_messageid_within_other_domain(self):
        _ = MessageIDFactory('test')
        msg = _(u'foo', u'foovalue ${testid1}')
        msg.mapping={u'testid1' : 'barvalue'}
        translated = self.TS.translate('other', msg)
        self.assertEquals(u'foovalue barvalue', translated,
                          'translation is not working. Got: %s' % translated)

    def test_translate_messageid_with_domain_overridden(self):
        _ = MessageIDFactory('testing')
        msg = _(u'id', u'value')
        msg.domain='test'
        translated = self.TS.translate('testing', msg)
        self.assertEquals(u'value', translated,
                          'translation is not working. Got: %s' % translated)

    def tearDown(self):
        tearDown()

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(Z3I18NCornerTestCase))
    return suite

if __name__ == '__main__':
    framework()

