try:
    from Products.Localizer.Localizer import manage_addLocalizer
    from Products.Localizer.MessageCatalog import manage_addMessageCatalog
    import Products.TranslationService
    hasLocalizer = 1
except ImportError:
    hasLocalizer = 0

try:
    import Products.i18n
    hasi18n = 1
except:
    hasi18n = 0

from zLOG import INFO, ERROR
from SetupBase import SetupWidget

class LocalizerLanguageSetup(SetupWidget):
    lName = 'Localizer'
    mName = 'Plone'
    tName = 'translation_service'
    type = 'Localizer Language Setup'
   
    description = """Sets up languages from the plone i18n project
using  Localizer and Translation Service"""
    
    def active(self):      
        reason = []
        if not hasLocalizer:
            reason.append("""Localizer and TranslationService are not installed, these products
must be installed for this to work. Localizer can be found at 
"http://www.zope.org/Members/jdavid/Localizer":http://www.zope.org/Members/jdavid/Localizer
and TranslationService can be found at 
"http://www.zope.org/Members/efge/TranslationService":http://www.zope.org/Members/efge/TranslationService.""")
        if not hasi18n:
            reason.append("""The plone i18n language pack is not installed, 
this can be found at 
"http://sourceforge.net/projects/plone-i18n":http://sourceforge.net/projects/plone-i18n.""")
        
        if self.lName not in self.portal.objectIds('Localizer') or \
            self.tName not in self.portal.objectIds('Translation Service'):
            reason.append("""The Localizer and TranslationService objects have not been installed
if you have these products installed into you must run the setup method to have them installed""")

        if reason: return "\n".join(reason)
        else: return 1

    def setup(self):
        portal = self.portal
    
        out = []
        out.append(('Installing Localizer', INFO))

        if self.lName not in portal.objectIds():
            manage_addLocalizer(portal, self.lName, 'en')

        if self.tName not in portal.objectIds():
            portal.manage_addProduct['TranslationService'].addPlacefulTranslationService(self.tName)

        tObj = portal._getOb(self.tName)
        lObj = portal._getOb(self.lName)

        # nuke out the accept_path
        lObj.accept_methods = ['accept_cookie',]

        manage_addMessageCatalog(lObj, 'Plone', 'Plone Message Catalog', 'en')
        mObj = lObj.Plone

        tObj.manage_setDomainInfo(None, path_0='%s/Plone' % self.lName) 

        # delete all languages, just in case
        # set the default language to english       
        mObj.manage_delLanguages(languages=mObj._languages)
        mObj.manage_changeDefaultLang(language='en')
        return out

    def delItems(self, languages):
        out = []
        mObj = self.portal.Localizer.Plone
        mObj.manage_delLanguages(languages=languages)
        out.append(('Deleted languages', ERROR))
        return out

    def addItems(self, languages):    
        out = []
        mObj = self.portal._getOb('Localizer').Plone
        for language in languages:
            file = Products.i18n.getFile(language)
            try:
                file = Products.i18n.getFile(language)
                mObj.manage_addLanguage(language)
                mObj.manage_import(language, file)
                out.append(('Adding language: %s' % language, INFO))
            except:
                out.append(('Failed to setup .po file for: %s' % file, ERROR))

        return out

    def installed(self):
        try:
            return self.portal._getOb('Localizer').Plone._languages
        except AttributeError:
            return []

    def available(self):
        return Products.i18n.listLanguages()
