.. include:: _robot.rst


.. code:: robotframework
   :class: hidden

   *** Test Cases ***

   Show add files menu
       Go to  ${PLONE_URL}

       Wait until element is visible
       ...  css=span.icon-plone-contentmenu-factories
       Click element  css=span.icon-plone-contentmenu-factories
       Wait until element is visible
       ...  css=#plone-contentmenu-factories li.plone-toolbar-submenu-header

       Mouse over  file
       Update element style  portal-footer  display  none

       Capture and crop page screenshot
       ...  ${CURDIR}/_robot/adding-files_add-menu.png
       ...  css=div.plone-toolbar-container
       ...  css=#plone-contentmenu-factories ul




.. code:: robotframework
   :class: hidden

   *** Test Cases ***

   Show new file add form
       Page should contain element  file
       Click link  file

       Wait until element is visible
       ...  css=#form-widgets-title

       Capture and crop page screenshot
       ...  ${CURDIR}/_robot/adding-files_add-form.png
       ...  css=#content

