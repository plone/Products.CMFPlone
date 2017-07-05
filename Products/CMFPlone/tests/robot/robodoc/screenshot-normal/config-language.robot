.. include:: _robot.rst

.. code:: robotframework
   :class: hidden

   *** Test Cases ***

   Show Language setup screen
       Go to  ${PLONE_URL}/@@language-controlpanel
       Capture and crop page screenshot
       ...  ${CURDIR}/_robot/language-setup.png
       ...  css=#content

       Click link  autotoc-item-autotoc-1
       Capture and crop page screenshot
       ...  ${CURDIR}/_robot/language-negotiation.png
       ...  css=#content
