.. include:: _robot.rst

.. code:: robotframework
   :class: hidden

   *** Test Cases ***

   Show Mail setup screen
       Go to  ${PLONE_URL}/@@mail-controlpanel
       Capture and crop page screenshot
       ...  ${CURDIR}/_robot/mail-setup.png
       ...  css=#content

