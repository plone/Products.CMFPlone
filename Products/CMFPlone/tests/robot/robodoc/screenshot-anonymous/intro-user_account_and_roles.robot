.. include:: _robot_anon.rst

.. code:: robotframework
   :class: hidden

   *** Keywords ***

   Highlight link
       [Arguments]  ${locator}
       Update element style  ${locator}  padding  0.5em
       Highlight  ${locator}

   *** Test Cases ***

   Take annotated screenshot
       Go to  ${PLONE_URL}
       Highlight link  css=#personaltools-login
       Capture and crop page screenshot
       ...    ${CURDIR}/_robot/anonymous-surfing.png
       ...    css=#content-header
       ...    css=#above-content-wrapper


.. code:: robotframework
   :class: hidden

       Enable autologin as  Manager
       ${user_id} =  Translate  user_id
       ...  default=jane-doe
       ${user_fullname} =  Translate  user_fullname
       ...  default=Jane Doe
       Create user  ${user_id}  Member  fullname=${user_fullname}
       Set autologin username  ${user_id}

   *** Test Cases ***

   Take logged in screenshot
       Go to  ${PLONE_URL}
       Capture and crop page screenshot
       ...    ${CURDIR}/_robot/loggedin-surfing.png
       ...    css=#above-content-wrapper
       ...    css=div.plone-toolbar-container

