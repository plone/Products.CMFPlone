.. include:: _robot.rst

.. code:: robotframework
   :class: hidden

   *** Test Cases ***

   Show socialmedia setup screen
       Go to  ${PLONE_URL}/@@social-controlpanel
       Capture and crop page screenshot
       ...  ${CURDIR}/_robot/social-setup.png
       ...  css=#content

