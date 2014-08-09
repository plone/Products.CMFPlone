# This module contains the global patterns settings

from zope.interface import implements
from zope.component import getAdapters
from zope.component import getUtility
from zope.component.hooks import getSite
from zope.publisher.browser import BrowserView

from plone.registry.interfaces import IRegistry

from .interfaces import IPatternsSettings
from .interfaces import IPatternsSettingsRenderer

import json


class PatternsSettings(BrowserView):
    implements(IPatternsSettingsRenderer)

    def __call__(self):
        modal_options = {
            'actionOptions': {
                'displayInModal': False,
            }
        }
        base_url = getSite().absolute_url()
        result = {
            'data-pat-modal': json.dumps(modal_options),
            'data-base-url': self.context.absolute_url(),
            'data-portal-url': base_url,
            'data-i18ncatalogurl': base_url + '/plonejsi18n'
        }
        adapters = getAdapters((self.context, self.request), IPatternsSettings)
        [result.update(x[1]()) for x in adapters]
        return result


class TinyMceSettingsAdapter(object):
    implements(IPatternsSettings)

    def __init__(self, context, request):
        self.request = request
        self.context = context
        self.registry = getUtility(IRegistry)
        self.settings = self.registry.get('Products.CMFPlone.TinyMCEsettings')
        self.config = {
            'portal_url': 'http://localhost:8080/Plone',
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
        configuration = {}
        for key, item in self.settings.items():
            if item.startswith('json:'):
                try:
                    configuration[key] = json.loads(item.lstrip('json:') % self.config)
                except:
                    configuration[key] = {}
            else:
                configuration[key] = item % self.config
        return {'data-pat-tinymce': json.dumps(configuration)}

