from AccessControl import getSecurityManager
from plone.memoize.view import memoize
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zExceptions.ExceptionFormatter import format_exception
from zope.component import getMultiAdapter

import json
import sys


class ExceptionView(BrowserView):
    basic_template = ViewPageTemplateFile('templates/basic_error_message.pt')

    def is_manager(self):
        return getSecurityManager().checkPermission(
            'Manage portal', self.context)

    @property
    @memoize
    def plone_redirector_view(self):
        return getMultiAdapter(
            (self.__parent__, self.request), name="plone_redirector_view"
        )

    def __call__(self):
        exception = self.context
        error_type = exception.__class__.__name__
        if error_type == "NotFound" and self.plone_redirector_view.attempt_redirect():
            # if a redirect is possible attempt_redirect returns True
            # and sets the proper location header
            return

        self.context = self.__parent__
        request = self.request

        exc_type, value, traceback = sys.exc_info()
        error_tb = ''.join(
            format_exception(exc_type, value, traceback, as_html=False))
        request.response.setStatus(exc_type)

        # Indicate exception as JSON
        if "text/html" not in request.getHeader('Accept', ''):
            request.response.setHeader("Content-Type", "application/json")
            return json.dumps({
                'error_type': error_type,
            })

        # Render page with user-facing error notice
        request.set('disable_border', True)
        request.set('disable_plone.leftcolumn', True)
        request.set('disable_plone.rightcolumn', True)

        try:
            return self.index(
                error_type=error_type,
                error_tb=error_tb)
        except:
            return self.basic_template(
                error_type=error_type,
                error_tb=error_tb)
