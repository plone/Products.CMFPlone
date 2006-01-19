#
# Zope 3.1-style messagefactory module for Zope <= 2.9 (Zope 3.1)
#

# BBB: Zope 2.8 / Zope X3.0

from zope.i18nmessageid import MessageIDFactory
msg_factory = MessageIDFactory('plone')

def PloneMessageFactory(ustr, default=None, mapping=None):
    message = msg_factory(ustr, default)
    if mapping is not None:
        message.mapping.update(mapping)
    return message

