.. include:: _robot.rst

.. code:: robotframework
   :class: hidden

   *** Test Cases ***

   Show ZODB maintenance setup screen
       Go to  ${PLONE_URL}/@@maintenance-controlpanel
       Capture and crop page screenshot
       ...  ${CURDIR}/_robot/zodb-setup.png
       ...  css=#content

