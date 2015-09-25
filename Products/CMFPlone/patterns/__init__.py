from borg.localrole.interfaces import IFactoryTempFolder
from Products.CMFPlone.interfaces import IPatternsSettings
from Products.CMFPlone.interfaces import ITinyMCESchema
from Products.CMFPlone.interfaces import ILinkSchema
from zope.interface import implements
from plone.registry.interfaces import IRegistry
from zope.component import getUtility
import json
from Products.CMFPlone.patterns.utils import get_portal_url
from Products.CMFCore.interfaces._content import IFolderish
from plone.uuid.interfaces import IUUID
from Products.CMFPlone.interfaces import IPloneSiteRoot
from Acquisition import aq_parent, aq_inner
from plone.app.theming.utils import theming_policy
from Products.CMFCore.utils import getToolByName
from zope.component.hooks import getSite


class TinyMCESettingsGenerator(object):

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.portal = getSite()
        registry = getUtility(IRegistry)
        self.settings = registry.forInterface(
            ITinyMCESchema, prefix="plone", check=False)
        self.portal_url = get_portal_url(self.portal)

    def get_theme(self):
        return theming_policy().get_theme()

    def get_content_css(self):
        files = [
            '%s/++plone++static/plone-compiled.css' % self.portal_url,
            '%s/++plone++static/tinymce-styles.css' % self.portal_url
        ]
        content_css = self.settings.content_css or []
        for url in content_css:
            files.append('%s/%s' % (self.portal_url, url))
        theme = self.get_theme()
        if (theme and hasattr(theme, 'tinymce_content_css') and
                theme.tinymce_content_css):
            files.append(self.portal_url + theme.tinymce_content_css)

        return ','.join(files)

    def get_style_format(self, txt, _type='format', base=None):
        parts = txt.strip().split('|')
        if len(parts) < 2:
            return
        if base is None:
            val = {}
        else:
            val = base
        val.update({
            'title': parts[0],
            _type: parts[1]
        })
        if len(parts) > 2:
            val['icon'] = parts[2]
        return val

    def get_all_style_formats(self):
        header_styles = self.settings.header_styles or []
        block_styles = self.settings.block_styles or []
        inline_styles = self.settings.inline_styles or []
        alignment_styles = self.settings.alignment_styles or []
        table_styles = self.settings.table_styles or []
        return [{
            'title': 'Headers',
            'items': [self.get_style_format(t) for t in header_styles]
        }, {
            'title': 'Block',
            'items': [self.get_style_format(t) for t in block_styles]
        }, {
            'title': 'Inline',
            'items': [self.get_style_format(t) for t in inline_styles]
        }, {
            'title': 'Alignment',
            'items': [self.get_style_format(t) for t in alignment_styles]
        }, {
            'title': 'Tables',
            'items': [self.get_style_format(t, 'classes', {'selector': 'table'})
                      for t in table_styles]
        }]

    def get_tiny_config(self):
        settings = self.settings

        tiny_config = {
            'resize': settings.resizing and 'both' or False,
            'content_css': self.get_content_css(),
            'plugins': ['plonelink', 'ploneimage', 'importcss'] + settings.plugins,
            'external_plugins': {},
            'toolbar': settings.toolbar,
            'entity_encoding': settings.entity_encoding,
            'importcss_append': True,
            'importcss_file_filter': '%s/++plone++static/tinymce-styles.css' % (
                self.portal_url)
        }
        toolbar_additions = settings.custom_buttons or []

        if settings.editor_height:
            tiny_config['height'] = settings.editor_height
        if settings.autoresize:
            tiny_config['plugins'].append('autoresize')
            tiny_config['autoresize_max_height'] = 1000  # hard coded?
        if settings.editor_width:
            tiny_config['width'] = settings.editor_width

        # specific plugin options
        if 'contextmenu' in settings.plugins:
            tiny_config['contextmenu'] = "plonelink ploneimage inserttable | cell row column deletetable"  # noqa

        theme = self.get_theme()
        if theme and getattr(theme, 'tinymce_styles_css', None):
            tiny_config['importcss_file_filter'] += ',%s/%s' % (
                self.portal_url,
                theme.tinymce_styles_css.lstrip('/'))

        if settings.libraries_spellchecker_choice == 'AtD':
            mtool = getToolByName(self.portal, 'portal_membership')
            member = mtool.getAuthenticatedMember()
            member_id = member.getId()
            if member_id:
                if 'compat3x' not in tiny_config['plugins']:
                    tiny_config['plugins'].append('compat3x')
                tiny_config['external_plugins']['AtD'] = \
                    '%s/++plone++static/tinymce-AtD-plugin/editor_plugin.js' % self.portal_url  # noqa
                # None when Anonymous User
                tiny_config['atd_rpc_id'] = 'plone-' + member_id
                tiny_config['atd_rpc_url'] = self.portal_url
                tiny_config['atd_show_types'] = ','.join(settings.libraries_atd_show_types)  # noqa
                tiny_config['atd_ignore_strings'] = ','.join(settings.libraries_atd_ignore_strings)  # noqa
                toolbar_additions.append('AtD')
        elif settings.libraries_spellchecker_choice == 'AtD':
            tiny_config['browser_spellcheck'] = True

        if toolbar_additions:
            tiny_config['toolbar'] += ' | %s' % ' '.join(toolbar_additions)

        for plugin in settings.custom_plugins or []:
            parts = plugin.split('|')
            if len(parts) != 2:
                continue
            tiny_config['external_plugins'][parts[0]] = parts[1]

        tiny_config['style_formats'] = self.get_all_style_formats()
        if settings.formats:
            tiny_config['formats'] = json.loads(settings.formats)

        if settings.menubar:
            tiny_config['menubar'] = settings.menubar
        if settings.menu:
            tiny_config['menu'] = json.loads(settings.menu)

        if hasattr(settings, 'templates') and settings.templates:
            try:
                tiny_config['templates'] = json.loads(settings.templates)
            except ValueError:
                pass

        return tiny_config


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

        registry = getUtility(IRegistry)
        settings = registry.forInterface(
            ILinkSchema, prefix="plone", check=False)

        msl = settings.mark_special_links
        elonw = settings.external_links_open_new_window
        if msl or elonw:
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

        generator = TinyMCESettingsGenerator(self.context, self.request)
        settings = generator.settings

        folder = aq_inner(self.context)
        # Test if we are currently creating an Archetype object
        if IFactoryTempFolder.providedBy(aq_parent(folder)):
            folder = aq_parent(aq_parent(aq_parent(folder)))
        if not IFolderish.providedBy(folder):
            folder = aq_parent(folder)

        if IPloneSiteRoot.providedBy(folder):
            initial = None
        else:
            initial = IUUID(folder, None)
        current_path = folder.absolute_url()[len(generator.portal_url):]

        image_types = settings.image_objects or []
        folder_types = settings.contains_objects or []
        configuration = {
            'relatedItems': {
                'vocabularyUrl':
                    '%s/@@getVocabulary?name=plone.app.vocabularies.Catalog' % (
                        generator.portal_url)
            },
            'upload': {
                'initialFolder': initial,
                'currentPath': current_path,
                'baseUrl': generator.portal_url,
                'relativePath': '@@fileUpload',
                'uploadMultiple': False,
                'maxFiles': 1,
                'showTitle': False
            },
            'base_url': self.context.absolute_url(),
            'tiny': generator.get_tiny_config(),
            # This is for loading the languages on tinymce
            'loadingBaseUrl': '%s/++plone++static/components/tinymce-builded/js/tinymce' % generator.portal_url,  # noqa
            'prependToUrl': 'resolveuid/',
            'linkAttribute': 'UID',
            'prependToScalePart': '/@@images/image/',
            'folderTypes': folder_types,
            'imageTypes': image_types
            # 'anchorSelector': utility.anchor_selector,
        }

        return {'data-pat-tinymce': json.dumps(configuration)}
