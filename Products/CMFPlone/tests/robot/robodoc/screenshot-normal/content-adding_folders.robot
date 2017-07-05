Adding Folders
==============

.. include:: _robot.rst

Adding folders to a Plone web site is the basic way of controlling the organization of content.

You have undoubtedly created folders (directories) on your computer's hard drive.
Personal computers use a hierarchy of folders to structure and organize the programs and files on the hard drive.
In Plone folders are essentially used the same way, except that they are created on a Plone web site, for organizing content in Plone's built-in storage system.

Folders are added by clicking the **Add new...** drop-down menu.
Select **Folder** from the menu:



.. code:: robotframework
   :class: hidden

   *** Test Cases ***

   Show add new folder menu
       Go to  ${PLONE_URL}

       Wait until element is visible
       ...  css=span.icon-plone-contentmenu-factories
       Click element  css=span.icon-plone-contentmenu-factories

       Wait until element is visible
       ...  css=#plone-contentmenu-factories li.plone-toolbar-submenu-header

       Mouse over  folder
       Update element style  portal-footer  display  none

       Capture and crop page screenshot
       ...  ${CURDIR}/_robot/adding-folders_add-menu.png
       ...  css=div.plone-toolbar-container
       ...  css=#plone-contentmenu-factories ul

.. figure:: /_robot/adding-folders_add-menu.png
   :align: center
   :alt: add-new-menu.png

You should now see the *Add Folder* screen:


.. code:: robotframework
   :class: hidden

   *** Test Cases ***

   Show new folder add form
       Page should contain element  folder
       Click link  folder

       Wait until element is visible
       ...  css=#form-widgets-IDublinCore-title

       Capture and crop page screenshot
       ...  ${CURDIR}/_robot/adding-folders_add-form.png
       ...  css=#content

.. figure:: /_robot/adding-folders_add-form.png
   :align: center
   :alt:


Fill in the **Title**, which is required, as indicated by the red dot.
The **Summary** is optional; you can always come back to the edit panel if you need to add a description of the folder.
Summaries are useful when a site visitor uses the search tool included with Plone - results will display with both the Title and Summary of the item.

You also notice tabs along the top:

-  *Default*, for entering the Title and Description fields,
-  *Categorization,* for specifying categories that apply to the folder
   (you may know these as *keywords*),
-  *Dates*, for setting the time period when the folder should be
   available for view on the web site,
-  *Ownership*, for specifying the creator and/or contributors for the
   content item,
-  *Settings,* for allowing comments about the item, enabling :ref:`rst_prev-next-links`,
   and choosing whether it shows in the navigation menu for the web
   site.

These tabs are standard, so you'll see them when you click other content types.
We will cover these tabs in another section of this user manual.

Be sure to click **Save** at the bottom of the page when you are finished.
This will complete the folder creation process.

