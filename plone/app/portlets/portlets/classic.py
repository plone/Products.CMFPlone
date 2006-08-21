from persistent import Persistent

from zope.interface import Interface, implements
from zope.component import adapts

from zope import schema

from zope.publisher.interfaces.browser import IBrowserRequest
from zope.publisher.interfaces.browser import IBrowserView

from plone.portlets.interfaces import IPortletDataProvider
from plone.portlets.interfaces import IPortletAssignment
from plone.portlets.interfaces import IPortletRenderer
from plone.portlets.interfaces import IPortletManager

from Acquisition import Explicit

from Products.Five.browser.pagetemplatefile import ZopeTwoPageTemplateFile

from Products.CMFPlone import PloneMessageFactory as _

class IClassicPortlet(IPortletDataProvider):
    """A portlet which can render a classic Plone portlet macro
    """
    
    template = schema.TextLine(title=_(u'Template'),
                               description=_(u'The template containing the portlet'),
                               required=True)
                               
    macro = schema.TextLine(title=_(u'Macro'),
                               description=_(u'The macro containing the portlet. Leave blank if there is no macro.'),
                               default=u'portlet',
                               required=True)
                               
class ClassicPortletAssignment(Persistent):
    implements(IClassicPortlet, IPortletAssignment)

    def __init__(self, template=u'', macro=u''):
        self.template = template
        self.macro = macro
        
    @property
    def available(self):
        return True
        
    @property
    def data(self):
        return self
        
    def __repr__(self):
        return '<ClassicPortlet rendering %s : %s>' % (self.template, self.macro,)

class ClassicPortletRenderer(Explicit):
    implements(IPortletRenderer)
    adapts(Interface, IBrowserRequest, IBrowserView, 
            IPortletManager, IClassicPortlet)
            
    def __init__(self, context, request, view, manager, data):
        self.context = context
        self.data = data

    def update(self):
        pass

    def use_macro(self):
        return bool(self.data.macro)
        
    def path_expression(self):
        expr = 'context/%s' % self.data.template
        if self.use_macro():
            expr += '/macros/%s' % self.data.macro
        return expr

    render = ZopeTwoPageTemplateFile('classic.pt')

    def __repr__(self):
        return '<ClassicPortletRenderer rendering %s>' % (self.path_expression(),)


