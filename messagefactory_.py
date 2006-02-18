#
# Zope 3.1-style messagefactory module for Zope < 2.9 (Zope 3.1)
# Also sets the default value for Zope >= 2.9 Messages to a sane value

try:
    from zope.i18nmessageid import MessageFactory
    imsg_factory = MessageFactory('plone')
    ZOPE28 = False
except ImportError:
    from zope.i18nmessageid import MessageIDFactory
    mmsg_factory = MessageIDFactory('plone')
    ZOPE28 = True

def MutableMessageFactory(ustr, default=None, mapping=None):
    message = mmsg_factory(ustr, default)
    if mapping is not None:
        message.mapping.update(mapping)
    return message

def ImmutableMessageFactory(ustr, default=None, mapping=None):
    # The default value is not automatically derived from ustr in zope 2.9+
    # so we need to do it manually
    if default is None:
        default = ustr
    message = imsg_factory(ustr, default=default, mapping=mapping)
    return message

if ZOPE28:
    PloneMessageFactory = MutableMessageFactory
else:
    PloneMessageFactory = ImmutableMessageFactory