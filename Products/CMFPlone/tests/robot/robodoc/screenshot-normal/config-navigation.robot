.. include:: _robot.rst

.. code:: robotframework
   :class: hidden

   *** Test Cases ***

   Show Navigation setup screen
       Go to  ${PLONE_URL}/@@navigation-controlpanel
       Capture and crop page screenshot
       ...  ${CURDIR}/_robot/navigation-setup.png
       ...  css=#content

