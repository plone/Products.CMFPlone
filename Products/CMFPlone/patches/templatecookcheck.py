# The implementation in zope.pagetemplate always checks for
# updated files unless python is run with -O, but we want to
# base this on the Zope2 debug mode flag.


from App.config import getConfiguration
from zope.pagetemplate.pagetemplatefile import PageTemplateFile

import logging
import os


def _cook_check(self):
    if self._v_last_read and not getConfiguration().debug_mode:
        return
    __traceback_info__ = self.filename
    try:
        mtime = os.path.getmtime(self.filename)
    except OSError:
        mtime = 0
    if self._v_program is not None and mtime == self._v_last_read:
        return
    text, type_ = self._read_file()
    self.pt_edit(text, type_)
    assert self._v_cooked
    if self._v_errors:
        logging.error(
            "PageTemplateFile: Error in template %s: %s",
            self.filename,
            "\n".join(self._v_errors),
        )
        return
    self._v_last_read = mtime


PageTemplateFile._cook_check = _cook_check
