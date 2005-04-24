import os

if not os.environ.get('ZOPETESTCASE'):
    import dependencies

from Products.CMFPlone import MigrationTool #:wort registerSetupWidget
from customization_policy import CustomizationPolicySetup
from ConfigurationMethods import GeneralSetup

MigrationTool.registerSetupWidget(CustomizationPolicySetup)
MigrationTool.registerSetupWidget(GeneralSetup)
