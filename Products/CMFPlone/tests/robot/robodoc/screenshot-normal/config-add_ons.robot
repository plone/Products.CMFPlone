.. include:: _robot.rst

.. code:: robotframework
   :class: hidden

   *** Test Cases ***

   Show Date setup screen
       Go to  ${PLONE_URL}/prefs_install_products_form
       Capture and crop page screenshot
       ...  ${CURDIR}/_robot/addon-setup.png
       ...  css=#content
