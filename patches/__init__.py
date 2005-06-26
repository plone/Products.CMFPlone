
import imagePatch               # WAII and 508 we need more properties on image
                                # objects

import zserverPatch             # Identify Plone in HTTP Headers - netcraft
                                # here we come!

import ceilingDatePatch         # Patch CMFCore's CEILING_DATE to fit into
                                # DateIndexes.

import httprequest_patch	# Add method to delete form data from a
                                # request, so a traverse to another
                                # template doesn't get confused.
