.. include:: _robot.rst

.. code:: robotframework
   :class: hidden

   *** Test Cases ***

   Show Image handling setup screen
       Go to  ${PLONE_URL}/@@imaging-controlpanel
       Capture and crop page screenshot
       ...  ${CURDIR}/_robot/imaging-setup.png
       ...  css=#content
