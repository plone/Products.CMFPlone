from Products.CMFPlone.interfaces import IPatternsSettings
from Products.CMFPlone.interfaces import ITinyMCESchema
from zope.interface import implements
from plone.registry.interfaces import IRegistry
from zope.component import getUtility
import json
from zope import component
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
from zope.component.hooks import getSite


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
            tiny: config,
            prependToUrl: 'resolveuid/',
            linkAttribute: 'UID',
            prependToScalePart: '/@@images/image/'
          })
        """
        registry = getUtility(IRegistry)
        settings = registry.forInterface(ITinyMCESchema, prefix="plone")
        portal_url = get_portal_url(self.context)
        config = {
            'portal_url': portal_url,
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
        portal = getSite()
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

        image_types = settings.imageobjects.splitlines()
        folder_types = settings.containsobjects.splitlines()

        tiny_config = {
            'resize': settings.resizing and 'both' or False,
            'content_css': content_css,
            'plugins': ['plonelink', 'ploneimage'] + settings.plugins,
            'external_plugins': {}
        }
        if settings.editor_height:
            tiny_config['height'] = settings.editor_height
        if settings.autoresize:
            tiny_config['plugins'].append('autoresize')
            tiny_config['autoresize_max_height'] = 1000  # hard coded?
        if settings.editor_width:
            tiny_config['width'] = settings.editor_width
        if 'contextmenu' in settings.plugins:
            tiny_config['contextmenu'] = "plonelink ploneimage inserttable | cell row column deletetable"  # noqa
        if settings.libraries_spellchecker_choice:
            tiny_config['plugins'].append('spellchecker')
            if settings.libraries_spellchecker_choice == 'AtD':
                mtool = getToolByName(portal, 'portal_membership')
                member = mtool.getAuthenticatedMember()
                if 'compat3x' not in tiny_config['plugins']:
                    tiny_config['plugins'].append('compat3x')
                tiny_config['external_plugins']['AtD'] = \
                    '%s/++plone++static/tinymce-AtD-plugin/editor_plugin.js' % portal_url
                # None when Anonymous User
                tiny_config['atd_rpc_id'] = 'Products.TinyMCE-' + (member.getId() or '')
                tiny_config['atd_rpc_url'] = "%s/@@" % portal_url
                tiny_config['atd_show_types'] = settings.libraries_atd_show_types.strip().replace('\n', ',')  # noqa
                tiny_config['atd_ignore_strings'] = settings.libraries_atd_ignore_strings.strip().replace('\n', ',')  # noqa

        configuration = {
            'relatedItems': {
                'vocabularyUrl': '%s/@@getVocabulary?name=plone.app.vocabularies.Catalog' % portal_url  # noqa
            },
            'upload': {
                'initialFolder': initial,
                'currentPath': current_path,
                'baseUrl': folder.absolute_url(),
                'relativePath': '@@fileUpload',
                'uploadMultiple': False,
                'maxFiles': 1,
                'showTitle': False
            },
            'base_url': config['document_base_url'],
            'tiny': tiny_config,
            # This is for loading the languages on tinymce
            'loadingBaseUrl': '++plone++static/components/tinymce-builded/js/tinymce',
            'prependToUrl': 'resolveuid/',
            'linkAttribute': 'UID',
            'prependToScalePart': '/@@images/image/',
            'folderTypes': folder_types,
            'imageTypes': image_types
            # 'anchorSelector': utility.anchor_selector,
        }

        return {'data-pat-tinymce': json.dumps(configuration)}
