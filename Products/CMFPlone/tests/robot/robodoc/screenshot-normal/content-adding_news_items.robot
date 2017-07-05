Adding News Items
======================

.. include:: _robot.rst

Plone web sites have a built-in system for publishing news items.

Use the *Add new...* menu for a folder to add a news item:

.. code:: robotframework
   :class: hidden

   *** Test Cases ***

   Show add new news-item menu
       Go to  ${PLONE_URL}

       Wait until element is visible
       ...  css=span.icon-plone-contentmenu-factories
       Click element  css=span.icon-plone-contentmenu-factories

       Wait until element is visible
       ...  css=#plone-contentmenu-factories li.plone-toolbar-submenu-header

       Mouse over  news-item
       Update element style  portal-footer  display  none

       Capture and crop page screenshot
       ...  ${CURDIR}/_robot/adding-news-items_add-menu.png
       ...  css=div.plone-toolbar-container
       ...  css=#plone-contentmenu-factories ul

.. figure:: /_robot/adding-news-items_add-menu.png
   :align: center
   :alt: add-new-news-item-menu.png

You will see the *Add News Item* panel:

.. code:: robotframework
   :class: hidden

   *** Test Cases ***

   Show new news-item edit form
       Page should contain element  news-item
       Click link  news-item

       Wait until element is visible
       ...  css=#mceu_16-body

       Capture and crop page screenshot
       ...  ${CURDIR}/_robot/adding-news-items_add-form.png
       ...  css=#content

.. figure:: /_robot/adding-news-items_add-form.png
   :align: center
   :alt:

The standard fields for title, description, and change note are in the panel, along with a visual editor area for body text and image and image caption fields.
You can be as creative as you want in the body text area, and you can use the insert image (upload image) function to add as much illustration as needed.
The images you upload for the news item will be added to the folder in which you are adding the news item.

The *Lead Image* and *Lead Image Caption* fields are for adding an image to be used as a representative graphic for the news item, for posting in news item listings.
The image will be automatically resized and positioned.
Use the **Body Text** to insert an image in the actual body of the News Item.

.. note::

    **IMPORTANT**: News items will not appear in the main web site news listing or news portlet until they are **published.**

