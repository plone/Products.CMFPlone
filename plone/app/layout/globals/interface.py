from zope.interface import Interface, implements
from plone.memoize.view import memoize

from Acquisition import aq_base
from Products.Five.browser import BrowserView

from interfaces import IInterfaceInformation

def resolveInterface(dotted_name):
    parts = dotted_name.split('.')
    m_name = '.'.join(parts[:-1])
    k_name = parts[-1]
    module = __import__(m_name, globals(), locals(), [k_name])
    klass = getattr(module, k_name)
    if not issubclass(klass, Interface):
        raise ValueError, '%r is not a valid Interface.' % dotted_name
    return klass

class InterfaceInformation(BrowserView):
    implements(IInterfaceInformation)
    
    @memoize
    def provides(self, dotted_name):
        iface = resolveInterface(dotted_name)
        return iface.providedBy(aq_base(self.context))

    @memoize
    def class_provides(self, dotted_name):
        iface = resolveInterface(dotted_name)
        return iface.providedBy(aq_base(self.context).__class__)