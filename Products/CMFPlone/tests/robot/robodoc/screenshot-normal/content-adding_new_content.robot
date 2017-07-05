Adding New Content
==================


.. include:: _robot.rst


A general overview of how to add new content items in Plone, including definitions of each standard content type

New content items are added via the **Add New . . .** drop-down menu:

.. code:: robotframework
   :class: hidden

   *** Test Cases ***

   Show add new content menu
       Go to  ${PLONE_URL}

       Wait until element is visible
       ...  css=span.icon-plone-contentmenu-factories
       Click element  css=span.icon-plone-contentmenu-factories

       Wait until element is visible
       ...  css=#plone-contentmenu-factories li.plone-toolbar-submenu-header

       Mouse over  document
       Update element style  portal-footer  display  none

       Capture and crop page screenshot
       ...  ${CURDIR}/_robot/adding-content_add-menu.png
       ...  css=div.plone-toolbar-container
       ...  css=#plone-contentmenu-factories ul

.. figure:: /_robot/adding-content_add-menu.png
   :align: center
   :alt: add-new-menu.png

Adding content in Plone is done *placefully*, which means you should navigate to the section of your Plone website where you want the new content to reside **before** you use the **Add New . . .** drop-down menu.
You can of course cut, copy, and paste content items from one section to another if needed at any later time.

Content Types
-------------

In Plone, you can use a number of **Content Types** to post certain kinds of content.
For example, to upload an image you must use the **Image** content type.
Below is a list of the available content types in order of their appearance, and what each are used for:

Collection
    Collections are used to group and display content based on a set of **criteria** which you can set. Collections work much like a query does in a database.
Event
    An Event is a content type specifically for posting information about an event (such as a fundraiser, meeting, barbecue, etc).
    This content type has a function which allows the site visitor to add the event to their desktop calendar. This includes applications such as: Google Calendar, Outlook, Sunbird and others.
    To add a single event to your calendar, click on the iCal link next to the "Add event to calendar" text in the main view of the event item.

    .. figure:: ../../_static/events-summary-chart.png
       :align: center
       :alt: events-summary-chart.png



    You can also get all the events in a folder in one go (currently only available in iCal format).
    To download the iCal file, append *@@ics\_view* to the end of the URL of the folder or collection containing the events.
    For example, if you want to get all the events from the *events* folder in the root of your site,go to *http://example.com/events/@@ics\_view*.

File
    A File in Plone is any binary file you wish to upload with the intent to be downloaded by your site visitors. Common examples are PDFs, Word Documents, and spreadsheets.
Folder
    Folders work in Plone much like they do on your computer. You can use folders to organize your content, and to give your Plone website a navigation structure.
Image
    The Image content type is used for uploading image files (JPG, GIF, PNG) so that you can insert them into pages or other page-like content types.
Link
    Also referred to as the 'Link Object'; do not confuse this with the links you create with the visual editor on pages or other content types.
    The Link content type is often used to include a link to an external website in Navigation and other specialized uses.
News Item
    This content type is similar to a Page, only a News Item is specifically for posting news.
    You can also attach a thumbnail image to a News Item, which then appears in folder summary views next to the summary of the News Item.
Page
    A Page in Plone is the basic content types.
    Use Pages to write the bulk of your web pages on your Plone website.

Note: Depending on what add-on products you have installed, you may see more options in your **Add New . . .** drop-down menu than appear here.
For information about those additional content types, refer to the Product documentation for the add-on in question.

Title
-----

Nearly all content types in Plone have two fields in common: **Title** and **Description.**

The **Title** of content items, including folders, images, pages, etc., can be anything you want -- you can use any keyboard characters, including spaces.
**Titles** become part of web address for each item you create in Plone.
Web addresses, also known as URLs, are what you type in a web browser to go to a specific location in a web site (Or, you would click your way there), such as:

www.mysite.com/about/personnel/sally/bio

or

www.mysite.com/images/butterflies/skippers/long-tailed-skippers

Web addresses *do* have restrictions on allowed keyboard characters, and spaces are not allowed.
Plone does a good job of keeping web addresses correct by using near-equivalents of the **Title** that you provide, by converting them to lowercase, and by substituting dashes for spaces and
other punctuation.

The web address of a given item is referred to as the **short name** in Plone.
When you use the **Rename** function, you'll see the short name along with the title.

The fields will vary according to the content type.
For instance, the Link content type has the URL field.
The File content type has the File field, and so on.

Description
-----------

The **Description** appears at the top of pages, just under the Title.
Descriptions are often used to conjunction with a variety of Folder and Collection views (such as Standard and Summary).
The Description also appears in search results via Plone's native search engine.

The Description is just plain text, without any form of mark-up. This is to keep it inline with the :term:`Dublin Core` standard, a long-established way of categorizing information.
