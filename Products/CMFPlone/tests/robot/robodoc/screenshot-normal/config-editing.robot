.. include:: _robot.rst

.. code:: robotframework
   :class: hidden

   *** Test Cases ***

   Show Editing setup screen
       Go to  ${PLONE_URL}/@@editing-controlpanel
       Capture and crop page screenshot
       ...  ${CURDIR}/_robot/editing-setup.png
       ...  css=#content

