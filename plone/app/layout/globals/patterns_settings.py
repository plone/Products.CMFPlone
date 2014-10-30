# This module contains the global patterns settings

from zope.interface import implements
from zope.component import getAdapters
from zope.component.hooks import getSite
from zope.publisher.browser import BrowserView
from .interfaces import IPatternsSettingsRenderer
from Products.CMFPlone.interfaces import IPatternsSettings

import json


class PatternsSettings(BrowserView):
    """
    Default patterns settings
    """
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
        adapters = getAdapters((self.context, self.request, None), IPatternsSettings)
        [result.update(x[1]()) for x in adapters]
        return result


