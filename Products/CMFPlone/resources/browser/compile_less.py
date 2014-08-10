import os
import subprocess
from Products.Five.browser import BrowserView
from Products.CMFCore.utils import getToolByName
from plone.memoize import ram
import logging

from Acquisition import aq_inner
from Products.PythonScripts.standard import url_quote
from Products.Five.browser import BrowserView
from Products.CMFCore.utils import getToolByName

import tempfile
import os
from zope.component.hooks import getSite

less_file = """
@import (less) url(%s/@@plone-mixins.less);
@import (less) url(%s);
"""


def render_cachekey(method, self, resource_id):
    """Cache by resource id"""
    return resource_id


class Opt(object):
    def __init__(self):
        self.minify = False
        self.xminify = False
        self.tabs = True


class CompileLess(BrowserView):

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.logger = logging.getLogger(__name__)

    def __call__(self):
        url = self.request.get('url', None)
        portal = getSite()
        if url:
            # Generate less file with mixins.less
            to_compile = less_file % (portal.absolute_url(), url)
            return self.compile_less_code(self._get_lessc_cmd(), to_compile)
        else:
            return "NO VALID URL"

    def _get_lessc_cmd(self):
        lessc_command_line = os.path.join(os.environ.get('INSTANCE_HOME'), os.path.pardir, os.path.pardir, 'bin', 'lessc')
        if not os.path.exists(lessc_command_line):
            self.logger.error("A valid lessc executable cannot be found."
                         "We are assumming that it has been provided by buildout"
                         "and placed in the buildout bin directory."
                         "If not, you should provide one (e.g. symbolic link) and place it there.")
        return lessc_command_line

    @ram.cache(render_cachekey)
    def compile_less_resource_id(self, resource_id):
        resource_inline = self.getInlineLess(resource_id)
        result = self.compile_less_code(self._get_lessc_cmd(), resource_inline)
        self.logger.info("The resource %s has been server-side compiled." % resource_id)
        return result

    def compile_less_code(self, lessc_command_line, less_code):
        """Compiles less code via the lessc compiler installed in bin/.

        This procedure returns the compiled css code that results of
        the compilation of the code as a string. Errors are
        discarded and not returned back.
        """

        # Call the LESSC executable
        process = subprocess.Popen([lessc_command_line, '-'],
                           stdout=subprocess.PIPE,
                           stdin=subprocess.PIPE)
        output, errors = process.communicate(input=less_code)
        # Return the command output
        return output


class compiledCSSView(BrowserView):
    """ View for server-side compiling of the LESS resources in portal_less
"""

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.logger = logging.getLogger('collective.lesscss')

    def portal_less(self):
        return getToolByName(self.context, 'portal_less')
                    

    def getInlineLess(self, item_id):
        """ Get the less code of a registered resource as a string

item_id: This is the id of the resource that we want to get
the content from.

return: The actual content of the stored resource is returned
in a string"""
        portal_less = self.portal_less()
        inline_code = portal_less.getInlineResource(item_id, self.context)
        return inline_code

    def _get_lessc_cmd(self):
        lessc_command_line = os.path.join(os.environ.get('INSTANCE_HOME'), os.path.pardir, os.path.pardir, 'bin', 'lessc')
        if not os.path.exists(lessc_command_line):
            self.logger.error("A valid lessc executable cannot be found."
                         "We are assumming that it has been provided by buildout"
                         "and placed in the buildout bin directory."
                         "If not, you should provide one (e.g. symbolic link) and place it there.")
        return lessc_command_line

    def __call__(self):
        portal_less = self.portal_less()

        less_resources = portal_less.getEvaluatedResources(self.context)

        results = []

        for less_resource in less_resources:
            
            res_id = less_resource.getId()
            compiled_css = self.compile_less_resource_id(res_id)

            results.append('/* %s */\n' % res_id)
            results.append(compiled_css)
            results.append('\n/* End %s */\n' % res_id)
            
        self.request.response.setHeader('Content-Type', 'text/css')
        return ''.join(results)

    @ram.cache(render_cachekey)
    def compile_less_resource_id(self, resource_id):
        resource_inline = self.getInlineLess(resource_id)
        result = self.compile_less_code(self._get_lessc_cmd(), resource_inline)
        self.logger.info("The resource %s has been server-side compiled." % resource_id)
        return result

    def compile_less_code(self, lessc_command_line, less_code):
        """Compiles less code via the lessc compiler installed in bin/.

This procedure returns the compiled css code that results of
the compilation of the code as a string. Errors are
discarded and not returned back.
"""

        # Call the LESSC executable
        process = subprocess.Popen([lessc_command_line, '-'],
                           stdout=subprocess.PIPE,
                           stdin=subprocess.PIPE)
        output, errors = process.communicate(input=less_code)
        # Return the command output
        return output



