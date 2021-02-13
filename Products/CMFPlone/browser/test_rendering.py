# -*- coding: utf-8 -*-
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class TestRenderingView(BrowserView):

    template = ViewPageTemplateFile('templates/test_rendering.pt')

    def __call__(self):
        self.request.set('disable_plone.rightcolumn', 1)
        self.request.set('disable_plone.leftcolumn', 1)
        return self.template()
