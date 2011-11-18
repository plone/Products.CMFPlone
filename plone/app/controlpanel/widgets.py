from zope.app.form.browser import MultiSelectWidget
from zope.app.form.browser import DropdownWidget
from zope.app.form.browser.widget import renderElement
from zope.component import getMultiAdapter
from zope.component import queryMultiAdapter
from zope.schema.interfaces import ITitledTokenizedTerm
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary

from Products.CMFPlone import PloneMessageFactory as _
from plone.app.form.widgets import MultiCheckBoxWidget

WEEKDAYS = (('Monday', 0),
            ('Tuesday', 1),
            ('Wednesday', 2),
            ('Thursday', 3),
            ('Friday', 4),
            ('Saturday', 5),
            ('Sunday', 6))


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


class MultiCheckBoxColumnsWidget(MultiCheckBoxWidget):
    """ """

    how_many_columns = 2   # two by default

    def __init__(self, field, request):
        """Initialize the widget."""
        super(MultiCheckBoxColumnsWidget, self).__init__(field,
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
        cc = self.how_many_columns
        breaks = [length % cc == 0 and length / cc or length / cc + 1]
        for b in range(2, cc):
            breaks.append(breaks[0] * b)

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

            if count in breaks:
                rendered_items.append('</div><div style="float:left; '
                                      'margin-right: 2em;">')

        rendered_items.append('</div><div style="clear:both">&nbsp;</div>')

        return rendered_items


class MultiCheckBoxThreeColumnWidget(MultiCheckBoxColumnsWidget):
    """ """
    how_many_columns = 3


class LanguageTableWidget(MultiCheckBoxWidget):
    """ """

    _joinButtonToMessageTemplate = u"""<tr class="%s">
<td>%s</td><td>%s</td><td>%s</td>
</tr>"""

    _table_start_template = u"""
<table summary="%s"
       class="listing"
       id="lang-selection"
       style="display: block; height: 20em; width: 50em; overflow: auto;">
    <thead>
        <tr>
            <th class="nosort">%s</th>
            <th>%s</th>
            <th>%s</th>
        </tr>
    </thead>
    <tbody>
    """

    _table_end_template = u"""</tbody></table>"""

    def associateLabelWithInputControl(self):
        return None

    def __init__(self, field, request):
        """Initialize the widget."""
        super(LanguageTableWidget, self).__init__(field,
            field.value_type.vocabulary, request)
        # TODO: This is a bit hairy, but seems to work fine.
        context = self.context.context.context
        portal_state = queryMultiAdapter((context, request),
                                         name=u'plone_portal_state')
        self.languages = portal_state.locale().displayNames.languages
        self.territories = portal_state.locale().displayNames.territories

    def renderValue(self, value):
        return ''.join(self.renderItems(value))

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

        rendered_items.append(self._table_start_template % (
            self.translate(_(u'heading_allowed_languages',
                             default=u'Allowed languages')),
            self.translate(_(u'heading_language_allowed',
                             default=u'Allowed?')),
            self.translate(_(u'heading_language',
                             default=u'Language')),
            self.translate(_(u'heading_language_code',
                             default=u'Code'))
            ))

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

        # Render normal values
        vocabulary = [(self.textForValue(term), term) for
                      term in self.vocabulary]

        # Sort by translated name, this is lame and needs proper collation
        # support, but we don't have that yet.
        vocabulary.sort()

        for item_text, term in vocabulary:
            if term.value in values:
                render = self.renderSelectedItem
            else:
                render = self.renderItem

            css = count % 2 and cssClass + 'even' or cssClass + 'odd'
            rendered_item = render(count,
                item_text,
                term.token,
                self.name,
                css)

            rendered_items.append(rendered_item)
            count += 1

        rendered_items.append(self._table_end_template)

        return rendered_items

    def renderItem(self, index, text, value, name, cssClass):
        id = '%s.%s' % (name, index)
        el = renderElement('input',
                             type="checkbox",
                             cssClass=cssClass,
                             name=name,
                             id=id,
                             value=value)
        return self._joinButtonToMessageTemplate % (cssClass, el, text, value)

    def renderSelectedItem(self, index, text, value, name, cssClass):
        id = '%s.%s' % (name, index)
        el = renderElement('input',
                             type="checkbox",
                             cssClass=cssClass,
                             name=name,
                             id=id,
                             value=value,
                             checked="checked")
        return self._joinButtonToMessageTemplate % (cssClass, el, text, value)

    def textForValue(self, term):
        """Extract a string from the `term`.

        The `term` must be a vocabulary tokenized term.
        """
        if ITitledTokenizedTerm.providedBy(term):
            if '-' in term.value:
                code, territory = term.value.split('-')
                territory = territory.upper()
                result = self.languages.get(code, None)
                # If we don't have a translation for the language, return the
                # English one and don't bother with the country name
                if result is None or result == code:
                    return term.title
                territory = self.territories.get(territory, territory)
                result = "%s (%s)" % (result, territory)
            else:
                result = self.languages.get(term.value, None)
                # If we don't have a translation for the language, return the
                # default English text, rather than the language code
                if result is None or result == term.value:
                    return term.title
            return result
        return term.token


class MultiSelectTupleWidget(MultiSelectWidget):
    """Provide a selection list for the tuple to be selected."""

    def _toFieldValue(self, input):
        value = super(MultiSelectWidget, self)._toFieldValue(input)
        if isinstance(value, list):
            value = tuple(value)
        return value


def WeekdayWidget(field, request):
    """A widget for the selection of weekdays."""
    weekdays = WEEKDAYS
    locale = None
    context = getattr(field, 'context', None)
    if context is not None:
        context = getattr(context, 'context', None)
        if context is not None:
            portal_state = getMultiAdapter((context, request),
                                           name=u'plone_portal_state')
            locale = portal_state.locale()
    if locale is not None:
        # We probably shouldn't assume a gregorian calendar here, but the rest
        # of our stack doesn't support anything else anyways for now.
        gregorian = locale.dates.calendars.get('gregorian')
        weekdays = tuple(zip(gregorian.getDayNames(), range(0, 8)))

    terms = [SimpleTerm(item[1], title=item[0]) for item in weekdays]
    return DropdownWidget(field, SimpleVocabulary(terms), request)


class AllowedTypesWidget(MultiCheckBoxWidget):
    """ A widget for activating and deactivating mimetypes with special
        considerations for types
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
