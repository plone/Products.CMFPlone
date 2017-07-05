.. include:: _robot.rst

.. code:: robotframework
   :class: hidden

   *** Test Cases ***

   Show Configuration Registry screen
       Go to  ${PLONE_URL}/portal_registry
       Capture and crop page screenshot
       ...  ${CURDIR}/_robot/configuration-registry.png
       ...  css=#content
