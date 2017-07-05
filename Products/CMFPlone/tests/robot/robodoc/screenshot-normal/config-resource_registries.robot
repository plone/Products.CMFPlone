.. include:: _robot.rst

.. code:: robotframework
   :class: hidden

   *** Test Cases ***

   Show Resource Registry screen
       Go to  ${PLONE_URL}/@@resourceregistry-controlpanel
       Capture and crop page screenshot
       ...  ${CURDIR}/_robot/resource-registry.png
       ...  css=#content
       Click link  Less Variables
       Capture and crop page screenshot
       ...  ${CURDIR}/_robot/less-variables.png
       ...  css=#content

