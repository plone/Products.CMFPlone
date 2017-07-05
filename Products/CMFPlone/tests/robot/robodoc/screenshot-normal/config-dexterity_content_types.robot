.. include:: _robot.rst

.. code:: robotframework
   :class: hidden

   *** Test Cases ***

   Show Dexterity setup screen
       Go to  ${PLONE_URL}/@@dexterity-types
       Capture and crop page screenshot
       ...  ${CURDIR}/_robot/dexterity-setup.png
       ...  css=#content

