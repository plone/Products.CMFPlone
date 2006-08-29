# import hacks
from unicodehacks import _nulljoin
from unicodehacks import _unicode_replace
from unicodehacks import FasterStringIO

# import the poor victims of our monkey patches
from zope.tal import talinterpreter
from zope.pagetemplate import pagetemplate

# Enable use of utf-8 text in tales inserts, until all code is changed to use
# pure Unicode only. This will only work for sites with a portal encoding of
# utf-8 but it will give us some time to change Archetypes and Plone
talinterpreter.unicode = _unicode_replace

# Deal with the case where Unicode and encoded strings occur on the same tag.
talinterpreter._nulljoin_old = talinterpreter._nulljoin
talinterpreter._nulljoin = _nulljoin

# Deal with the case of tal snippets encoded as utf-8 and those being Unicode.
# These are joined using a the getValue method of a StringIO class.
talinterpreter.TALInterpreter.StringIO = FasterStringIO
pagetemplate.StringIO = FasterStringIO
