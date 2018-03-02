# -*- coding: utf-8 -*-
from AccessControl import getSecurityManager
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zExceptions.ExceptionFormatter import format_exception
from zope.component.hooks import getSite

import json
import sys


class ExceptionView(BrowserView):
    basic_template = ViewPageTemplateFile('templates/basic_error_message.pt')

    def is_manager(self):
        return getSecurityManager().checkPermission(
            'Manage portal', self.context)

    def __call__(self):
        exception = self.context
        self.context = self.__parent__
        request = self.request

        error_type = exception.__class__.__name__
        exc_type, value, traceback = sys.exc_info()
        error_tb = ''.join(
            format_exception(exc_type, value, traceback, as_html=True))
        request.response.setStatus(exc_type)

        # Indicate exception as JSON
        if "text/html" not in request.getHeader('Accept', ''):
            request.response.setHeader("Content-Type", "application/json")
            return json.dumps({
                'error_type': error_type,
            })

        if getSite() is None:
            # We cannot get the site, so we cannot render our nice template
            template = self.basic_template
        else:
            # Use a simplified template if main_template is not renderable
            try:
                main = self.context.unrestrictedTraverse('main_template')
                main()
            except:
                template = self.basic_template
            else:
                template = self.index

        # Render page with user-facing error notice
        request.set('disable_border', True)
        request.set('disable_plone.leftcolumn', True)
        request.set('disable_plone.rightcolumn', True)

        return template(
            error_type=error_type,
            error_tb=error_tb,
        )
