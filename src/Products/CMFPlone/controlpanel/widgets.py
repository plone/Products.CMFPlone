from z3c.form.browser.checkbox import CheckBoxWidget
from z3c.form.interfaces import NO_VALUE
from z3c.form.widget import FieldWidget


class ReverseCheckBoxWidget(CheckBoxWidget):
    """Checkbox widget where you uncheck the options you want to select."""

    def isChecked(self, term):
        return term.token not in self.value

    def extract(self, default=NO_VALUE):
        tokens = [t.token for t in self.terms]
        if (
            self.name not in self.request
            and self.name + "-empty-marker" in self.request
        ):
            return tokens
        value = self.request.get(self.name, default)
        if value == default:
            return value
        if not isinstance(value, (tuple, list)):
            value = (value,)
        for token in value:
            if token in tokens:
                tokens.remove(token)
        return tokens


def ReverseCheckBoxFieldWidget(field, request):
    return FieldWidget(field, ReverseCheckBoxWidget(request))
