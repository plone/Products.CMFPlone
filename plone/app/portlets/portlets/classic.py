from zope.interface import implements

from plone.portlets.interfaces import IPortletDataProvider
from plone.app.portlets.portlets import base

from zope import schema
from zope.formlib import form
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

class Assignment(base.Assignment):
    implements(IClassicPortlet)

    def __init__(self, template=u'', macro=u''):
        self.template = template
        self.macro = macro

    @property
    def title(self):
        return self.template

class Renderer(base.Renderer):

    def __init__(self, context, request, view, manager, data):
        self.context = context
        self.data = data

    render = ZopeTwoPageTemplateFile('classic.pt')
    
    def use_macro(self):
        return bool(self.data.macro)

    def path_expression(self):
        expr = 'context/%s' % self.data.template
        if self.use_macro():
            expr += '/macros/%s' % self.data.macro
        return expr

class AddForm(base.AddForm):
    form_fields = form.Fields(IClassicPortlet)

    def create(self, data):
        return Assignment(template=data.get('template', ''),
                          macro=data.get('macro', ''))

class EditForm(base.EditForm):
    form_fields = form.Fields(IClassicPortlet)