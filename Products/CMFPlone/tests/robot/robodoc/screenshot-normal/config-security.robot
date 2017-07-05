.. include:: _robot.rst

.. code:: robotframework
   :class: hidden

   *** Test Cases ***

   Show Security setup screen
       Go to  ${PLONE_URL}/@@security-controlpanel
       Capture and crop page screenshot
       ...  ${CURDIR}/_robot/security-setup.png
       ...  css=#content

