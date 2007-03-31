import unittest
import doctest

def test_safe_render():
    r"""
    Render the portlet safely, so that when an exception
    occurs, we log and don't bail out.

    >>> from plone.app.portlets.portlets.base import Renderer
    >>> class Stub: pass
    >>> renderer = Renderer(*(None,) * 5)
    >>> renderer.aq_inner = Stub()
    >>> renderer.aq_inner.aq_parent = Stub()
    >>> renderer.aq_inner.aq_parent.error_log = Stub()
    >>> def raising(exc_info):
    ...     print exc_info
    >>> def error_message():
    ...     print "Error message was called."
    >>> renderer.aq_inner.aq_parent.error_log.raising = raising
    >>> renderer.error_message = error_message
    >>> renderer.safe_render() # doctest: +NORMALIZE_WHITESPACE +ELLIPSIS
    (<class exceptions.NotImplementedError at ...>,
     <exceptions.NotImplementedError instance at ...>,
     <traceback object at ...>)
    Error message was called.
    """

def test_suite():
    return unittest.TestSuite((doctest.DocTestSuite()))
