from Products.CMFPlone import utils

import json
import warnings


def format_pattern_settings(option, config):
    if option.startswith("json:"):
        try:
            return json.loads(option.lstrip("json:") % config)
        except:
            return {}
    return option % config


def get_portal():
    """DEPRECATED"""
    warnings.warn(
        "Instead of Products.CMFPlone.patterns.get_portal: "
        "use Products.CMFPlone.utils.get_portal",
        DeprecationWarning,
    )
    return utils.get_portal()


def get_portal_url(context):
    """DEPRECATED"""
    warnings.warn(
        "Instead of Products.CMFPlone.patterns.get_portal_url: "
        "Use Products.CMFPlone.utils.portal.absolute_url()",
        DeprecationWarning,
    )
    return utils.get_portal().absolute_url()
