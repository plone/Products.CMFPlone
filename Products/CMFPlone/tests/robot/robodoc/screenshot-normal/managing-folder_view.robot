===========
Folder View
===========

Folders have the "Display" item on the Toolbar, which controls the different ways of showing folder contents.


.. include:: _robot.rst

.. code:: robotframework
   :class: hidden

   *** Test Cases ***

   Show display menu
       Go to  ${PLONE_URL}

       Click link  css=#plone-contentmenu-display a

       Wait until element is visible
       ...  css=#plone-contentmenu-display li.plone-toolbar-submenu-header


       Update element style  portal-footer  display  none

       Capture and crop page screenshot
       ...  ${CURDIR}/_robot/display-menu.png
               ...  css=#content-header
               ...  css=div.plone-toolbar-container

.. figure:: /_robot/display-menu.png
   :align: center
   :alt: Display menu



For most content items, if you want to change how it looks, you edit the content directly.
But folders are a different animal.
As containers of other items, folders can display their contents in a variety of ways.


Plone by default comes with these displays:

Standard view
   A basic list of contained items, showing their title, description, modification date and icon.
   (The icon and the modification date may or may not be shown to anonymous visitors, depending on your site settings)
Summary view
   A slightly nicer view, showing the Title and Description and a 'Read more' link for each content item. If the contained items have a 'Lead Image' declared, like the standard News Item, it will show a thumbnail of that image as well.
Tabular view
   Compact view, as a table, of the contained items.
All content
   This displays the full content of each contained item. This can quickly get very long, and is best used only on folders with a small number of items in them, and where each item is in itself not too long. An example could be a list of Frequently Asked Questions, or FAQ.
Album view
   This view is meant for folders with images in them, it shows a thumbnail for every content item.
Event Listing
   Designed to give a nice overview of a series of Events.

And often the most useful, yet also more difficult to understand:

**"Select a content item as default view"**


.. note::

   The standard folder views are often used as the starting point for more elaborate views, that will reflect the purpose of the website.
   At the very least, these views are often customized with CSS or :term:`Diazo` rules, to show specific information about the content types shown. Many add-ons will provide extra folder views, to properly display any special content items that these add-ons provide. Some widely used add-ons provide a so-called 'faceted search' display, which is designed to quickly find your way around large numbers of content.

   Therefore, you will likely see more possibilities in this menu if you are working on a real-life site.


Setting an Individual Content Item as the View for a Folder
-----------------------------------------------------------

The basic list view functionality described above for folders fits the normal way we think of folders -- as containers of items -- but Plone adds a nice facility to set the view of a folder to be that of any single item contained within the folder.

You can set the display view for a folder to show a single page, which can be useful for showing an 'introductory page', which you or others have created to explain the purpose of this section of the site, and which contains links to sub-sections and other documents.

Or, you can set it to a *"collection"*, which on its own is already a powerful content filter. One common use-case, and one that is used in a default Plone site, is to have a Folder called "News". In it, there are individual News items, but also a Collection which will sort all of these news items so the most recent one is shown first.

You would then set the "most recent" collection as the default view of the "News" folder. Using the same 'Display' menu, you can then set the display view for the "most recent" to be the "Summary view"


A word of warning
-----------------

Setting the default view of a folder to be one of the items contained in that folder, is one of the most powerful features of Plone.

But the very fact that you can select for instance a 'Collection', which in term displays a whole number of items, as that default item, can also be confusing.

This will play a role when you edit a Folder, which has a content item set as its default view. Or when you want to manage the portlets for a Folder which has a content item set as its default view. Or when you are trying to give :doc:`sharing permissions </working-with-content/collaboration-and-workflow/collaboration-through-sharing>` on a folder, but by accident are only setting them on the default item in that folder.

Plone will display a message in these cases, along the lines of "You are editing the default view of a container. If you wanted to edit the container itself, go *here*."

**Learn to not ignore, but read those messages!**

Remember: when setting properties, ask yourself the question: *do I want to do this on the Folder, or just on this one content item that is contained in the Folder?*



Lastly, the display view setting should be used with care, because it can do two things:

- It changes the behavior of folders, from acting as simple containers to acting as direct links to content, if you select an individual content item as default view.
- Changing the view can radically alter the way the information is presented to users. If you select "Album view" on a folder with no images, it may appear the content is gone, since there are no images to show, although of course the information is still there. Or your perfectly written introductory page is suddenly replaced by a boring tabular display.

While the "Display" menu is one of the most powerful features of Plone, it is wise to note for yourself which was the previous view - before you change it - so you can quickly change it back when needed.


