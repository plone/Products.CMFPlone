from Products.CMFPlone.Portal import listPolicies, custom_policies
from zLOG import INFO, ERROR
from SetupBase import SetupWidget
from types import StringType
from ZODB.POSException import ConflictError

import sys
import traceback

from Products.CMFPlone.utils import log_deprecated
log_deprecated("CustomizationPolicies are deprecated and will be removed in "
               "Plone 3.0. Please use GenericSetup extension profiles instead.")

class CustomizationPolicySetup(SetupWidget):
    type = 'Customization Policy Setup'
    single = 1
    description = """Sets up a customization policy, which configures
    the plone setup. The default site has already been run.
    <b>Please note</b> that uninstalling a policy is
    <i>not</i> supported at this time.
    Be careful before selecting this."""

    def delItems(self, policy):
        out = []
        out.append(('Currently we have no way to remove '
                    'customisation policies', ERROR))
        return out

    def addItems(self, policy):
        assert len(policy) == 1, "There must only be one policy set at a time."

        out = []
        c = custom_policies[policy[0]]
        try:
            res = c.customize(self.portal)
            if res:
                if isinstance(res, StringType):
                    for line in res.split('\n'):
                        out.append((line, INFO))
                    else:
                        out.extend(res)

            out.append(("The customisation policy has been applied", INFO))
        except ConflictError: 
            raise
        except:
            out.append(("An error has occured", INFO))
            for line in traceback.format_tb(sys.exc_traceback):
                out.append((line, ERROR))

        return out

    def installed(self):
        return []

    def available(self):
        return listPolicies
