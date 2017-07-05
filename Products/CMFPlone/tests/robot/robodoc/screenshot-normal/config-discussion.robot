.. include:: _robot.rst

.. code:: robotframework
   :class: hidden

   *** Test Cases ***

   Show Discussion setup screen
       Go to  ${PLONE_URL}/@@discussion-controlpanel
       Capture and crop page screenshot
       ...  ${CURDIR}/_robot/discussion-setup.png
       ...  css=#content

