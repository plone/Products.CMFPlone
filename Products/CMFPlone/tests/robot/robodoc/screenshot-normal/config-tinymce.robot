.. include:: _robot.rst

.. code:: robotframework
   :class: hidden

   *** Test Cases ***

   Show Mail setup screen
       Go to  ${PLONE_URL}/@@tinymce-controlpanel
       Capture and crop page screenshot
       ...  ${CURDIR}/_robot/tinymce-setup.png
       ...  css=#content
