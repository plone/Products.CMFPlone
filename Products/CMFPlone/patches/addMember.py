try:
    from Products.CMFPlone import patches  # noqa
except ImportError:
    pass

from Products.CMFCore.RegistrationTool import RegistrationTool
if hasattr(RegistrationTool.addMember.im_func, '__doc__'):
    del RegistrationTool.addMember.im_func.__doc__
