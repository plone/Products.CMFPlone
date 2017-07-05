.. include:: _robot.rst

.. code:: robotframework
   :class: hidden

   *** Test Cases ***

   Show Date setup screen
       Go to  ${PLONE_URL}/@@dateandtime-controlpanel
       Capture and crop page screenshot
       ...  ${CURDIR}/_robot/date-setup.png
       ...  css=#content

