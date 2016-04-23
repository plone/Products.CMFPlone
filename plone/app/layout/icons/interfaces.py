# -*- coding: utf-8 -*-
from zope.interface import Attribute
from zope.interface import Interface


class IContentIcon(Interface):
    """An icon for a piece of content
    """

    width = Attribute("The width of the icon (required).")

    height = Attribute("Returns the height of the icon (required).")

    url = Attribute("The absolute url of the icon. This should be "
                    "None if no icon should be rendered.")

    description = Attribute("The description used for the alt attribute. "
                            "Should be at least an empty string.")

    title = Attribute("The content of the title attribute. Should be None "
                      "if the title is empty.")

    def html_tag():
        """Return a HTML string that is the tag for rendering this icon.
        """
