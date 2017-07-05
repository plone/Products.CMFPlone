.. include:: _robot.rst

.. code:: robotframework
   :class: hidden

   *** Test Cases ***

   Show Site setup screen
       Go to  ${PLONE_URL}/@@overview-controlpanel
       Capture and crop page screenshot
       ...  ${CURDIR}/_robot/site-overview.png
       ...  css=#content

