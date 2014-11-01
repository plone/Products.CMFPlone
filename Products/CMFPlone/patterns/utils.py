import json
from zope.component.hooks import getSite
from plone.app.layout.navigation.root import getNavigationRootObject
from Products.CMFCore.interfaces import ISiteRoot
from zope.component import providedBy


def format_pattern_settings(option, config):
    if option.startswith('json:'):
        try:
            result = json.loads(option.lstrip('json:') % config)
        except:
            result = {}
    else:
        result = option % config
    return result


def get_portal():
    closest_site = getSite()
    if closest_site is not None:
        for potential_portal in closest_site.aq_chain:
            if ISiteRoot in providedBy(potential_portal):
                return potential_portal


def get_portal_url(context):
    portal = get_portal()
    if portal:
        root = getNavigationRootObject(context, portal)
        if root:
            try:
                return root.absolute_url()
            except AttributeError:
                return portal.absolute_url()
        else:
            return portal.absolute_url()
    return ''