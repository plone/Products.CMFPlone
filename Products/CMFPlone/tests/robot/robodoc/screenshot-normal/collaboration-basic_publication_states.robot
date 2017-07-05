.. include:: _robot.rst

.. code:: robotframework
   :class: hidden

   *** Test Cases ***

   Create sample content
       Go to  ${PLONE_URL}

       ${item} =  Create content  type=Document
       ...  id=samplepage  title=Sample Page
       ...  description=The long wait is now over
       ...  text=<p>Our new site is built with Plone.</p>


   Show state menu
       Go to  ${PLONE_URL}/samplepage

       Wait until element is visible
       ...  css=span.icon-plone-contentmenu-workflow
       Click element  css=span.icon-plone-contentmenu-workflow

       Wait until element is visible
       ...  css=#plone-contentmenu-workflow li.plone-toolbar-submenu-header

       Mouse over  workflow-transition-publish
       Update element style  portal-footer  display  none

       Capture and crop page screenshot
       ...  ${CURDIR}/_robot/workflow-basic.png
               ...  css=#content-header
               ...  css=div.plone-toolbar-container



.. code:: robotframework
   :class: hidden

   Show sendback
       Go to  ${PLONE_URL}/samplepage

       Wait until element is visible
       ...  css=span.icon-plone-contentmenu-workflow
       Click element  css=span.icon-plone-contentmenu-workflow

       Wait until element is visible
       ...  css=#plone-contentmenu-workflow li.plone-toolbar-submenu-header

       click link  workflow-transition-submit

       Go to  ${PLONE_URL}/samplepage

       Wait until element is visible
       ...  css=span.icon-plone-contentmenu-workflow
       Click element  css=span.icon-plone-contentmenu-workflow

       Wait until element is visible
       ...  css=#plone-contentmenu-workflow li.plone-toolbar-submenu-header

       Mouse over  workflow-transition-reject
       Update element style  portal-footer  display  none

       Capture and crop page screenshot
       ...  ${CURDIR}/_robot/workflow-reject.png
               ...  css=#content-header
               ...  css=div.plone-toolbar-container

