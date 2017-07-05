.. include:: _robot.rst

.. code:: robotframework
   :class: hidden

   *** Test Cases ***

   Show HTML filter setup screen
       Go to  ${PLONE_URL}/@@filter-controlpanel
       Capture and crop page screenshot
       ...  ${CURDIR}/_robot/filter-setup.png
       ...  css=#content

