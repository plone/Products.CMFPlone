.. include:: _robot.rst

.. code:: robotframework
   :class: hidden

   *** Test Cases ***

   Show Markup setup screen
       Go to  ${PLONE_URL}/@@markup-controlpanel
       Capture and crop page screenshot
       ...  ${CURDIR}/_robot/markup-setup.png
       ...  css=#content
