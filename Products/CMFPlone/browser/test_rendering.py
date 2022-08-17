# -*- coding: utf-8 -*-
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class TestRenderingView(BrowserView):

    template = ViewPageTemplateFile('templates/test_rendering.pt')

    def __call__(self):
        self.request.set('disable_plone.rightcolumn', 1)
        self.request.set('disable_plone.leftcolumn', 1)
        return self.template()


class TestRenderingCheatsheetView(BrowserView):

    template = ViewPageTemplateFile('templates/test_rendering_cheatsheet.pt')

    def __call__(self):
        self.request.set('disable_plone.rightcolumn', 1)
        self.request.set('disable_plone.leftcolumn', 1)
        return self.template()


class TestRenderingIconsView(BrowserView):

    template = ViewPageTemplateFile('templates/test_rendering_icons.pt')

    def __call__(self):
        self.request.set('disable_plone.rightcolumn', 1)
        self.request.set('disable_plone.leftcolumn', 1)
        return self.template()
