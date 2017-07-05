.. include:: _robot.rst

.. code:: robotframework
   :class: hidden

   *** Test Cases ***

   Show Theme setup screen
       Go to  ${PLONE_URL}/@@theming-controlpanel
       Capture and crop page screenshot
       ...  ${CURDIR}/_robot/theme-setup.png
       ...  css=#content

