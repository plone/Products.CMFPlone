# -*- coding: utf-8 -*-
from zope.deferredimport import deprecated

deprecated(
    "Import from Products.CMFPlone instead",
    DefaultPage='Products.CMFPlone.browser.defaultpage:DefaultPage',
    isDefaultPage='Products.CMFPlone.defaultpage:is_default_page',
    getDefaultPage='Products.CMFPlone.defaultpage:get_default_page',
)
