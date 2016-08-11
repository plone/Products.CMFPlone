# -*- coding: utf-8 -*-
from Acquisition import aq_inner
from Acquisition import aq_parent
from borg.localrole.interfaces import IFactoryTempFolder
from plone.app.layout.navigation.root import getNavigationRootObject
from plone.registry.interfaces import IRegistry
from plone.uuid.interfaces import IUUID
from Products.CMFCore.interfaces._content import IFolderish
from Products.CMFPlone.interfaces import ILinkSchema
from Products.CMFPlone.interfaces import IPatternsSettings
from Products.CMFPlone.interfaces import IPloneSiteRoot
from Products.CMFPlone.patterns.tinymce import TinyMCESettingsGenerator
from Products.CMFPlone.utils import get_portal
from zope.component import getUtility
from zope.interface import implementer
from zope.schema.interfaces import IVocabularyFactory

import json


@implementer(IPatternsSettings)
class PatternSettingsAdapter(object):
    """
    Provides default plone settings relevant for patterns.
    """

    def __init__(self, context, request, field):
        self.request = request
        self.context = context
        self.field = field

    def __call__(self):
        data = self.tinymce()
        data.update(self.mark_special_links())
        return data

    def mark_special_links(self):
        result = {}

        registry = getUtility(IRegistry)
        settings = registry.forInterface(
            ILinkSchema, prefix="plone", check=False)

        msl = settings.mark_special_links
        elonw = settings.external_links_open_new_window
        if msl or elonw:
            result = {
                'data-pat-markspeciallinks': json.dumps(
                    {
                        'external_links_open_new_window': elonw,
                        'mark_special_links': msl
                    }
                )
            }
        return result

    @property
    def image_scales(self):
        factory = getUtility(
            IVocabularyFactory,
            'plone.app.vocabularies.ImagesScales'
        )
        vocabulary = factory(self.context)
        ret = [{'title': it.title, 'value': it.value} for it in vocabulary]
        ret = sorted(ret, key=lambda it: it['title'])
        return json.dumps(ret)

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

        portal = get_portal()
        portal_url = portal.absolute_url()
        nav_root = getNavigationRootObject(folder, portal)
        nav_root_url = nav_root.absolute_url()
        current_path = folder.absolute_url()[len(portal_url):]

        image_types = settings.image_objects or []
        folder_types = settings.contains_objects or []

        server_url = self.request.get('SERVER_URL', '')
        site_path = portal_url[len(server_url):]
        configuration = {
            'base_url': self.context.absolute_url(),
            'imageTypes': image_types,
            'imageScales': self.image_scales,
            'linkAttribute': 'UID',
            # This is for loading the languages on tinymce
            'loadingBaseUrl': '{0}/++plone++static/components/tinymce-builded/'
                              'js/tinymce'.format(portal_url),
            'relatedItems': {
                'folderTypes': folder_types,
                'rootPath': '/'.join(nav_root.getPhysicalPath())
                            if nav_root else '/',
                'sort_on': 'sortable_title',
                'sort_order': 'ascending',
                'vocabularyUrl':
                    '{0}/@@getVocabulary?name=plone.app.vocabularies.'
                    'Catalog'.format(nav_root_url),
            },
            'prependToScalePart': '/@@images/image/',
            'prependToUrl': '{0}/resolveuid/'.format(site_path.rstrip('/')),
            'tiny': generator.get_tiny_config(),
            'upload': {
                'baseUrl': portal_url,
                'currentPath': current_path,
                'initialFolder': initial,
                'maxFiles': 1,
                'relativePath': '@@fileUpload',
                'showTitle': False,
                'uploadMultiple': False,
            },
        }
        return {'data-pat-tinymce': json.dumps(configuration)}
