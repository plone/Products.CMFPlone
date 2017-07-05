.. include:: _robot.rst

.. code:: robotframework
   :class: hidden

   *** Test Cases ***

   Show add collection menu
       Go to  ${PLONE_URL}
       Wait until element is visible
       ...  css=span.icon-plone-contentmenu-factories
       Click element  css=span.icon-plone-contentmenu-factories
       Wait until element is visible
       ...  css=#plone-contentmenu-factories li.plone-toolbar-submenu-header

       Mouse over  collection
       Update element style  portal-footer  display  none

       Capture and crop page screenshot
       ...  ${CURDIR}/_robot/adding-collections_add-menu.png
       ...  css=div.plone-toolbar-container
       ...  css=#plone-contentmenu-factories ul



.. code:: robotframework
   :class: hidden

   *** Test Cases ***

   select criteria
       Go to  ${PLONE_URL}/++add++Collection
       Click element  css=div.querystring-criteria-index a
       Capture and crop page screenshot
       ...  ${CURDIR}/_robot/collection-criteria.png
       ...  css=div.select2-drop-active
