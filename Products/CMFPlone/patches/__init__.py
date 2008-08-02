import zserverPatch             # Identify Plone in HTTP Headers - netcraft
                                # here we come!

import dateIndexPatch           # Avoid OverflowErrors in Date*Indexes

import interfacePatch           # Fixes for interfaces tests that need to
                                # be merged upstream at some point

import unicodeFallbackPatch     # Makes the TAL engine in Zope 2.10+ accept
                                # utf-8 encoded strings as well as Unicode

import csrf                     # Protects most important methods from
csrf.applyPatches()             # CSRF attacks
