from zope.interface import Invalid


def positiveNumber(val):
    if not isinstance(val, int):
        try:
            val = int(val)
        except:
            raise Invalid("Not a valid integer value")
    if val < 0:
        raise Invalid("Must enter a positive number")
    return True