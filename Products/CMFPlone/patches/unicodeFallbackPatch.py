# The following hacks make sure that Unicode and utf-8 encoded strings can be
# mixed in all page templates and tal snippets.

# While the general direction is to require Unicode in all places, we need to
# provide a gentle evolution path, as we cannot radically change this
# requirement and end up with lots of broken code. Our strategy is to allow
# only utf-8 encoded strings though in order to limit the performance impact
# instead of supporting all encodings.

# Therefor these patches will probably stay here for quite a while.

# import hacks
from .unicodehacks import new__call__
from .unicodehacks import _nulljoin
from .unicodehacks import _unicode_replace
from .unicodehacks import FasterStringIO

# import the poor victims of our monkey patches
from zope.tal import talinterpreter
from zope.tales import expressions
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

# Deal with the case of unicode tal expressions that have included parts
# encoded in utf-8. For example u'string:Select $item_title_or_id' where
# item_title_or_id is encoded in utf-8
expressions.StringExpr._old_call = expressions.StringExpr.__call__
expressions.StringExpr.__call__ = new__call__
