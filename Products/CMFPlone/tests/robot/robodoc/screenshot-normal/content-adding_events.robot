.. include:: _robot.rst


.. code:: robotframework
   :class: hidden

   *** Test Cases ***

   Show add new event menu
       Go to  ${PLONE_URL}

       Wait until element is visible
       ...  css=span.icon-plone-contentmenu-factories
       Click element  css=span.icon-plone-contentmenu-factories

       Wait until element is visible
       ...  css=#plone-contentmenu-factories li.plone-toolbar-submenu-header

       Mouse over  event
       Update element style  portal-footer  display  none

       Capture and crop page screenshot
       ...  ${CURDIR}/_robot/adding-events_add-menu.png
       ...  css=div.plone-toolbar-container
       ...  css=#plone-contentmenu-factories ul


.. code:: robotframework
   :class: hidden

   *** Test Cases ***

   Show new event add form
       Page should contain element  event
       Click link  event

       Wait until element is visible
       ...  css=#mceu_16-body
       Capture and crop page screenshot
       ...  ${CURDIR}/_robot/adding-events_add-form.png
       ...  css=#content

