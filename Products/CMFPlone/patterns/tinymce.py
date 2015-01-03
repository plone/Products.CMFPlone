from Products.CMFPlone.interfaces import IPatternsSettings
from Products.CMFPlone.interfaces import ITinyMCESchema
from zope.interface import implements
from plone.registry.interfaces import IRegistry
from zope.component import getUtility
import json
from Products.CMFPlone.patterns.utils import format_pattern_settings
from Products.CMFPlone.patterns.utils import get_portal_url
from Products.CMFCore.interfaces._content import IFolderish
from plone.uuid.interfaces import IUUID
from Products.CMFPlone.interfaces import IPloneSiteRoot
from Acquisition import aq_parent
from plone.app.theming.utils import getCurrentTheme
from plone.app.theming.utils import getTheme


class TinyMceSettingsAdapter(object):
    implements(IPatternsSettings)

    def __init__(self, context, request, field):
        self.request = request
        self.context = context
        self.field = field
        self.registry = getUtility(IRegistry)
        self.settings = self.registry.forInterface(ITinyMCESchema, prefix="plone")
        self.config = {
            'portal_url': get_portal_url(context),
            'document_base_url': self.context.absolute_url()
        }

    def __call__(self):
        """
        data-pat-tinymce : JSON.stringify({
            relatedItems: {
              vocabularyUrl: config.portal_url + '/@@getVocabulary?name=plone.app.vocabularies.Catalog'
            },
            rel_upload_path: '@@fileUpload',
            folder_url: config.document_base_url,
            tiny: config,
            prependToUrl: 'resolveuid/',
            linkAttribute: 'UID',
            prependToScalePart: '/@@images/image/'
          })
        """

        folder = self.context
        if not IFolderish.providedBy(self.context):
            folder = aq_parent(self.context)
        if IPloneSiteRoot.providedBy(folder):
            initial = None
        else:
            initial = IUUID(folder, None)
        current_path = folder.absolute_url()[len(self.config['portal_url']):]

        # Check if theme has a custom content css
        theme = getCurrentTheme()
        themeObj = getTheme(theme)
        if themeObj.tinymce_content_css:
            content_css = self.config['portal_url'] + themeObj.tinymce_content_css
        else:
            content_css = self.settings.content_css

        configuration = {
            'relatedItems': format_pattern_settings(
                self.settings.relatedItems,
                self.config),
            'upload': {
                'initialFolder': initial,
                'currentPath': current_path,
                'baseUrl': self.config['document_base_url'],
                'relativePath': format_pattern_settings(
                    self.settings.rel_upload_path,
                    self.config),
                'uploadMultiple': False,
                'maxFiles': 1,
                'showTitle': False
            },
            'base_url': self.config['document_base_url'],
            'tiny': {
                'content_css': content_css,
            },
            # This is for loading the languages on tinymce
            'loadingBaseUrl': '++plone++static/components/tinymce-builded/js/tinymce',
            'prependToUrl': 'resolveuid/',
            'linkAttribute': format_pattern_settings(
                self.settings.linkAttribute,
                self.config),
            'prependToScalePart': format_pattern_settings(
                self.settings.prependToScalePart,
                self.config),
            # XXX need to get this from somewhere...
            'folderTypes': ','.join(['Folder']),
            'imageTypes': ','.join(['Image']),
            #'anchorSelector': utility.anchor_selector,
            #'linkableTypes': utility.linkable.replace('\n', ',')
        }

        return {'data-pat-tinymce': json.dumps(configuration)}