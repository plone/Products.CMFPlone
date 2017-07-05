.. include:: _robot.rst

.. code:: robotframework
   :class: hidden

   *** Test Cases ***

   Show Syndication setup screen
       Go to  ${PLONE_URL}/@@syndication-controlpanel
       Capture and crop page screenshot
       ...  ${CURDIR}/_robot/syndication-setup.png
       ...  css=#content

