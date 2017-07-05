.. include:: _robot.rst

.. code:: robotframework
   :class: hidden

   *** Test Cases ***

   Show Date setup screen
       Go to  ${PLONE_URL}/@@search-controlpanel
       Capture and crop page screenshot
       ...  ${CURDIR}/_robot/search-setup.png
       ...  css=#content

