.. include:: _robot.rst

.. code:: robotframework
   :class: hidden

   *** Test Cases ***

   Show Error log setup screen
       Go to  ${PLONE_URL}/prefs_error_log_form
       Capture and crop page screenshot
       ...  ${CURDIR}/_robot/errorlog-setup.png
       ...  css=#content

