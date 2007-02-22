from zope.app.form.browser import MultiCheckBoxWidget
from zope.app.form.browser import MultiSelectWidget
from zope.app.form.browser import DropdownWidget
from zope.app.form.browser import RadioWidget
from zope.schema.vocabulary import SimpleVocabulary

from Products.CMFPlone import PloneMessageFactory as _


class DropdownChoiceWidget(DropdownWidget):
    """ """

    def __init__(self, field, request):
        """Initialize the widget."""
        super(DropdownChoiceWidget, self).__init__(field,
            field.vocabulary, request)


class MultiCheckBoxVocabularyWidget(MultiCheckBoxWidget):
    """ """

    def __init__(self, field, request):
        """Initialize the widget."""
        super(MultiCheckBoxVocabularyWidget, self).__init__(field,
            field.value_type.vocabulary, request)


class MultiCheckBoxThreeColumnWidget(MultiCheckBoxWidget):
    """ """

    def __init__(self, field, request):
        """Initialize the widget."""
        super(MultiCheckBoxThreeColumnWidget, self).__init__(field,
            field.value_type.vocabulary, request)

    def renderItemsWithValues(self, values):
        """Render the list of possible values, with those found in
        `values` being marked as selected.
        
        This code is mostly taken from from zope.app.form.browser.itemswidgets
        import ItemsEditWidgetBase licensed under the ZPL 2.1.
        """

        cssClass = self.cssClass

        # multiple items with the same value are not allowed from a
        # vocabulary, so that need not be considered here
        rendered_items = []
        count = 0

        # XXX remove the inline styles!
        rendered_items.append('<div style="float:left; margin-right: 2em;">')

        # Handle case of missing value
        missing = self._toFormValue(self.context.missing_value)

        if self._displayItemForMissingValue and not self.context.required:
            if missing in values:
                render = self.renderSelectedItem
            else:
                render = self.renderItem

            missing_item = render(count,
                self.translate(self._messageNoValue),
                missing,
                self.name,
                cssClass)
            rendered_items.append(missing_item)
            count += 1

        length = len(self.vocabulary)
        break1 = length % 3 == 0 and length / 3 or length / 3 + 1
        break2 = break1 * 2

        # Render normal values
        for term in self.vocabulary:
            item_text = self.textForValue(term)

            if term.value in values:
                render = self.renderSelectedItem
            else:
                render = self.renderItem

            rendered_item = render(count,
                item_text,
                term.token,
                self.name,
                cssClass)

            rendered_items.append(rendered_item)
            count += 1

            if (count == break1 or count == break2):
                rendered_items.append('</div><div style="float:left; '
                                      'margin-right: 2em;">')

        rendered_items.append('</div><div style="clear:both">&nbsp;</div>')

        return rendered_items



class MultiSelectTupleWidget(MultiSelectWidget):
    """Provide a selection list for the tuple to be selected."""

    def _toFieldValue(self, input):
        value = super(MultiSelectWidget, self)._toFieldValue(input)
        if isinstance(value, list):
            value = tuple(value)
        return value


def WeekdayWidget(field, request):
    """A widget for the selection of weekdays."""
    vocabulary = SimpleVocabulary.fromItems((('Monday', 0), 
                                             ('Tuesday', 1),
                                             ('Wednesday', 2),
                                             ('Thursday', 3),
                                             ('Friday', 4),
                                             ('Saturday', 5),
                                             ('Sunday', 6)))
    return DropdownWidget(field, vocabulary, request)


class AllowedTypesWidget(MultiCheckBoxWidget):
    """ A widget for activating and deactivating mimetypes with special considerations for types
        whose transformation is not installed locally.
        
        a format can have the following states:
        
         1. active (i.e. selected and deselectable)
         2. inactive (i.e. not selected but selectable)
         3. deactivated (i.e. not selected and not selectable)
         4. default (i.e. selected and not deselectable)
        
        TODO: 
         * computation of state for each format
         * rendering of those states
    """

    def __init__(self, field, request):
        """Initialize the widget."""
        super(AllowedTypesWidget, self).__init__(field,
            field.value_type.vocabulary, request)

