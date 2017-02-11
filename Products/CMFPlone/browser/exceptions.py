from AccessControl import getSecurityManager
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from six import reraise
from zExceptions.ExceptionFormatter import format_exception
from zope.security.interfaces import IUnauthorized
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

        # If running in the testbrowser with handleErrors=False,
        # avoid rendering exception view
        if not self.request.environ.get('wsgi.handleErrors', True):
            reraise(*sys.exc_info())

        error_type = exception.__class__.__name__
        error_tb = ''.join(format_exception(*sys.exc_info(), as_html=True))

        request = self.request
        response = self.request.response

        # Call PAS _unauthorized hook for Unauthorized exceptions
        is_unauthorized = IUnauthorized.providedBy(exception)
        if is_unauthorized and hasattr(response, '_unauthorized'):
            response._unauthorized()

        # Indicate exception as JSON
        if "text/html" not in request.getHeader('Accept', ''):
            request.response.setHeader("Content-Type", "application/json")
            return json.dumps({
                'error_type': error_type,
            })

        # Use a simplified template if main_template is not available
        try:
            self.context.unrestrictedTraverse('main_template')
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
