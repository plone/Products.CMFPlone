.. include:: _robot.rst


.. code:: robotframework
   :class: hidden

   *** Keywords ***

   Highlight field
       [Arguments]  ${locator}
       Update element style  ${locator}  padding  0.5em
       Highlight  ${locator}

   *** Test Cases ***

   Take annotated screenshot
       Go to  ${PLONE_URL}/@@site-controlpanel
       Highlight field  css=#formfield-form-widgets-site_logo
       Capture and crop page screenshot
       ...    ${CURDIR}/_robot/change-logo-in-site-control-panel.png
       ...    css=#content
       ...    css=#formfield-form-widgets-site_logo
