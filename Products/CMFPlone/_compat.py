# -*- coding: utf-8 -*-
import sys

if sys.version_info[0] < 3: #pragma NO COVER Python2

    PY2 = True
    PY3 = False

    from StringIO import StringIO
    BytesIO = StringIO
    import urlparse
    from urllib import urlencode
    import httplib as httpclient

    def _u(s, encoding='unicode_escape'):
        return unicode(s, encoding)

else: #pragma NO COVER Python3

    PY2 = False
    PY3 = True

    from io import StringIO
    from io import BytesIO

    import urllib.parse as urlparse  # noqa
    from urllib.parse import urlencode
    import http.client as httpclient  # noqa

    def _u(s, encoding=None):
        if encoding is None:
            return s
        return str(s, encoding)
