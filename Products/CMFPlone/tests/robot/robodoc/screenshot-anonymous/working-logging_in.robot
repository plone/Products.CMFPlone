.. include:: _robot_anon.rst


.. code:: robotframework
   :class: hidden

   *** Keywords ***

   Highlight link
       [Arguments]  ${locator}
       Update element style  ${locator}  padding  0.5em
       Highlight  ${locator}

   *** Test Cases ***

   Take login link screenshot
       Go to  ${PLONE_URL}
       Highlight link  css=#personaltools-login
       Capture and crop page screenshot
       ...    ${CURDIR}/_robot/login-link.png
       ...    css=#content-header
       ...    css=#above-content-wrapper



.. code:: robotframework
   :class: hidden

   *** Test Cases ***

   Take login screenshot
       Go to  ${PLONE_URL}/login
       Capture and crop page screenshot
       ...    ${CURDIR}/_robot/login-popup.png
       ...    css=#content-core
