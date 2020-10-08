# FIXME: This no longer works with the new ZMI
# from . import addzmiplonesite          # Add an explicit link to add a new Plone
# site to the ZMI for faster access

from . import addzmisecuritywarning    # Add a warning to the ZMI security tab
# that you shouldn't use it

from . import dateIndexPatch           # Avoid OverflowErrors in Date*Indexes

from . import unicodeFallbackPatch     # Makes the TAL engine in Zope 2.10+ accept
# utf-8 encoded strings as well as Unicode

from . import csrf                     # Protects most important methods from
csrf.applyPatches()             # CSRF attacks

from . import speed                    # Various caching patches to improve speed

from . import iso8601                  # use `DateTime.ISO8601` for `DateTime.ISO`
iso8601.applyPatches()

from . import sendmail
sendmail.applyPatches()

from . import templatecookcheck        # Make sure templates aren't re-read in
# production sites

from . import publishing

from . import z3c_form

from . import gtbn
