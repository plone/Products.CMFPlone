import os
import subprocess
from Products.Five.browser import BrowserView
from Products.CMFCore.utils import getToolByName
from plone.memoize import ram
import logging
from distutils.version import StrictVersion

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
            self.request.response.setHeader("Content-Type", "text/css")
            return self.compile_less_code(self._get_lessc_cmd(), to_compile)
        else:
            return "NO VALID URL"

    def _get_lessc_cmd(self):
        lessc_command_line = os.path.join(os.environ.get('INSTANCE_HOME'), os.path.pardir, os.path.pardir, 'bin', 'lessc')
        if not os.path.exists(lessc_command_line):
            try:
                out = subprocess.check_output(['lessc','-v'])
                version = out.split(' ')[1]
                if StrictVersion(version) > StrictVersion('1.7.0'):
                    lessc_command_line = 'lessc'
                else:
                    self.logger.error("A valid lessc executable cannot be found."
                                 "We found a version of less in your system but is too old."
                                 "We need 1.7.0 version minimum")
            except OSError:
                self.logger.error("A valid lessc executable cannot be found."
                             "We've tried to find it on the path or buildout bin folder")
        return lessc_command_line

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





