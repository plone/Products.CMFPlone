from Products.CMFPlone import PloneMessageFactory as _
from plone.app.registry.browser import controlpanel

from Products.CMFPlone.interfaces import IFilterSchema

#filtertagset = FormFieldsets(IFilterTagsSchema)
#filtertagset.id = 'filtertags'
#filtertagset.label = _(u'label_filtertags', default=u'Tags')
#
#filterattributes = FormFieldsets(IFilterAttributesSchema)
#filterattributes.id = 'filterattributes'
#filterattributes.label = _(u'label_filterattributes', default=u'Attributes')
#
#filtereditor = FormFieldsets(IFilterEditorSchema)
#filtereditor.id = 'filtereditor'
#filtereditor.label = _(u'filterstyles', default=u'Styles')
#
#tagattr_widget = CustomWidgetFactory(ObjectWidget, TagAttrPair)
#combination_widget = CustomWidgetFactory(ListSequenceWidget,
#                                         subwidget=tagattr_widget)


class FilterControlPanelForm(controlpanel.RegistryEditForm):

    id = "FilterControlPanel"
    label = _("HTML Filter settings")
    description = _("Plone filters HTML tags that are considered security "
                    "risks. Be aware of the implications before making "
                    "changes below. By default only tags defined in XHTML "
                    "are permitted. In particular, to allow 'embed' as a tag "
                    "you must both remove it from 'Nasty tags' and add it to "
                    "'Custom tags'. Although the form will update "
                    "immediately to show any changes you make, your changes "
                    "are not saved until you press the 'Save' button.")
    form_name = _("HTML Filter settings")
    schema = IFilterSchema
    schema_prefix = "plone"

#    form_fields = FormFieldsets(filtertagset, filterattributes, filtereditor)
#    form_fields['stripped_combinations'].custom_widget = combination_widget

    #form_fields = FormFieldsets(searchset)
    #form_fields['types_not_searched'].custom_widget = MCBThreeColumnWidget
    #form_fields['types_not_searched'].custom_widget.cssClass='label'

    def updateFields(self):
        super(FilterControlPanelForm, self).updateFields()


class FilterControlPanel(controlpanel.ControlPanelFormWrapper):
    form = FilterControlPanelForm
