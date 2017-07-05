.. include:: _robot.rst

.. code:: robotframework
   :class: hidden

   *** Test Cases ***

   Show Site setup screen
       Go to  ${PLONE_URL}/@@site-controlpanel
       Capture and crop page screenshot
       ...  ${CURDIR}/_robot/site-setup.png
       ...  css=#content

