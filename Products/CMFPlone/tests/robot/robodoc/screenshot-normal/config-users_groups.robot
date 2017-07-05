.. include:: _robot.rst

.. code:: robotframework
   :class: hidden

   *** Test Cases ***

   Show Users setup screen
       Go to  ${PLONE_URL}/@@usergroup-userprefs
       Capture and crop page screenshot
       ...  ${CURDIR}/_robot/users-setup.png
       ...  css=#content

       Go to  ${PLONE_URL}/@@usergroup-groupprefs
       Capture and crop page screenshot
       ...  ${CURDIR}/_robot/groups-setup.png
       ...  css=#content
       Go to  ${PLONE_URL}/@@usergroup-controlpanel
       Capture and crop page screenshot
       ...  ${CURDIR}/_robot/users-settings.png
       ...  css=#content
       Go to  ${PLONE_URL}/@@member-fields
       Capture and crop page screenshot
       ...  ${CURDIR}/_robot/users-fields.png
       ...  css=#content

