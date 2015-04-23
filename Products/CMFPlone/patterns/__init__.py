from Products.CMFPlone.interfaces import IPatternsSettings
from Products.CMFPlone.interfaces import ITinyMCESchema
from zope.interface import implements
from plone.registry.interfaces import IRegistry
from zope.component import getUtility
import json
from zope import component
from Products.CMFPlone.patterns.utils import format_pattern_settings
from Products.CMFPlone.patterns.utils import get_portal_url
from Products.CMFCore.interfaces._content import IFolderish
from plone.uuid.interfaces import IUUID
from Products.CMFPlone.interfaces import IPloneSiteRoot
from Acquisition import aq_parent
from plone.app.theming.utils import getCurrentTheme
from plone.app.theming.utils import getTheme
from Products.CMFCore.utils import getToolByName
from zope.ramcache.interfaces import ram
from plone.app.theming.utils import isThemeEnabled
from zope.component import queryMultiAdapter


class PloneSettingsAdapter(object):
    """
    This adapter will handle all default plone settings.

    Right now, it only does tinymce
    """
    implements(IPatternsSettings)

    def __init__(self, context, request, field):
        self.request = request
        self.context = context
        self.field = field

    def mark_special_links(self):
        result = {}
        properties = getToolByName(self.context, "portal_properties")
        props = getattr(properties, 'site_properties')

        if not props:
            return result
        msl = props.getProperty('mark_special_links', 'false')
        elonw = props.getProperty('external_links_open_new_window', 'false')
        if msl == 'true' or elonw == 'true':
            result = {'data-pat-markspeciallinks':
                      ('{"external_links_open_new_window": "%s",'
                       '"mark_special_links": "%s"}' % (elonw, msl))}
        return result

    def __call__(self):
        data = self.tinymce()
        data.update(self.mark_special_links())
        return data

    def tinymce(self):
        """
        data-pat-tinymce : JSON.stringify({
            relatedItems: {
              vocabularyUrl: config.portal_url +
                '/@@getVocabulary?name=plone.app.vocabularies.Catalog'
            },
            rel_upload_path: '@@fileUpload',
            folder_url: config.document_base_url,
            tiny: config,
            prependToUrl: 'resolveuid/',
            linkAttribute: 'UID',
            prependToScalePart: '/@@images/image/'
          })
        """
        registry = getUtility(IRegistry)
        settings = registry.forInterface(ITinyMCESchema, prefix="plone")
        config = {
            'portal_url': get_portal_url(self.context),
            'document_base_url': self.context.absolute_url()
        }

        folder = self.context
        if not IFolderish.providedBy(self.context):
            folder = aq_parent(self.context)
        if IPloneSiteRoot.providedBy(folder):
            initial = None
        else:
            initial = IUUID(folder, None)
        current_path = folder.absolute_url()[len(config['portal_url']):]

        # Check if theme has a custom content css
        portal_state = queryMultiAdapter((self.context, self.request), name=u"plone_portal_state")
        portal = portal_state.portal()
        # Volatile attribute to cache the current theme
        if hasattr(portal, '_v_currentTheme'):
            themeObj = portal._v_currentTheme
        else:
            theme = getCurrentTheme()
            themeObj = getTheme(theme)
            portal._v_currentTheme = themeObj
        cache = component.queryUtility(ram.IRAMCache)
        content_css = None
        if isThemeEnabled(self.request):
            themeObj = cache.query(
                'plone.currentTheme',
                key=dict(prefix='theme'),
                default=None)
            if themeObj is None:
                theme = getCurrentTheme()
                themeObj = getTheme(theme)
                cache.set(
                    themeObj,
                    'plone.currentTheme',
                    key=dict(prefix='theme'))
            if (themeObj and hasattr(themeObj, 'tinymce_content_css') and
                    themeObj.tinymce_content_css):
                content_css = config['portal_url'] + themeObj.tinymce_content_css

        if content_css is None:
            content_css = settings.content_css

        configuration = {
            'relatedItems': format_pattern_settings(
                settings.relatedItems,
                config),
            'upload': {
                'initialFolder': initial,
                'currentPath': current_path,
                'baseUrl': folder.absolute_url(),
                'relativePath': format_pattern_settings(
                    settings.rel_upload_path,
                    config),
                'uploadMultiple': False,
                'maxFiles': 1,
                'showTitle': False
            },
            'base_url': config['document_base_url'],
            'tiny': {
                'content_css': content_css,
            },
            # This is for loading the languages on tinymce
            'loadingBaseUrl': '++plone++static/components/tinymce-builded/js/tinymce',
            'prependToUrl': 'resolveuid/',
            'linkAttribute': format_pattern_settings(
                settings.linkAttribute,
                config),
            'prependToScalePart': format_pattern_settings(
                settings.prependToScalePart,
                config),
            # XXX need to get this from somewhere...
            'folderTypes': ','.join(['Folder']),
            'imageTypes': ','.join(['Image']),
            # 'anchorSelector': utility.anchor_selector,
            # 'linkableTypes': utility.linkable.replace('\n', ',')
        }

        return {'data-pat-tinymce': json.dumps(configuration)}
