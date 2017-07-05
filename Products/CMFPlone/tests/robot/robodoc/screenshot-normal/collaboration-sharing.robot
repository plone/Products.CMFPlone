.. include:: _robot.rst


.. code:: robotframework
   :class: hidden

   *** Test Cases ***

   Create sample content
       Go to  ${PLONE_URL}

       ${item} =  Create content  type=Folder
       ...  id=documentation  title=Documentation
       ...  description=Here you can find the documentation on our new product

   Show sharing menu

       Go to  ${PLONE_URL}/documentation

       Click link  css=#contentview-local_roles a

       Wait until element is visible
       ...  css=#user-group-sharing-container

       Update element style  portal-footer  display  none


      Capture and crop page screenshot
       ...  ${CURDIR}/_robot/sharing-menu.png
               ...  css=#content-header
               ...  css=div.plone-toolbar-container


