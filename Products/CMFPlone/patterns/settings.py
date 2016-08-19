# -*- coding: utf-8 -*-
from Acquisition import aq_parent, aq_inner
from borg.localrole.interfaces import IFactoryTempFolder
from plone.app.layout.navigation.root import getNavigationRootObject
from plone.registry.interfaces import IRegistry
from plone.uuid.interfaces import IUUID
from Products.CMFCore.interfaces._content import IFolderish
from Products.CMFPlone.interfaces import IImagingSchema
from Products.CMFPlone.interfaces import ILinkSchema
from Products.CMFPlone.interfaces import IPatternsSettings
from Products.CMFPlone.interfaces import IPloneSiteRoot
from Products.CMFPlone.utils import get_portal
from Products.CMFPlone.utils import safe_unicode
from Products.CMFPlone.patterns.tinymce import TinyMCESettingsGenerator
from zope.component import getUtility
from zope.interface import implementer

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

    def get_scales(self):
        """Format the list of scales ['mini 200:200', ...] into a string like
        'Mini (200x200):mini,...'  as expected by the tinymce-pattern.
        """
        results = []

        registry = getUtility(IRegistry)
        settings = registry.forInterface(
            IImagingSchema, prefix="plone", check=False)

        for scale in settings.allowed_sizes:
            parts = scale.split()
            name = parts[0].capitalize()
            size = parts[1].replace(':', 'x')
            scale_id = parts[0]
            results.append('{0} ({1}):{2}'.format(name, size, scale_id))
        return ','.join(results)

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
        scales = self.get_scales()

        server_url = self.request.get('SERVER_URL', '')
        site_path = portal_url[len(server_url):]
        configuration = {
            'base_url': self.context.absolute_url(),
            'imageTypes': image_types,
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
            'scales': scales,
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
