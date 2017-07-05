Setting Basic Properties
========================

.. include:: _robot.rst

The tab panels available on each content item has fields for basic information.
The more data you can provide, the better Plone can help in making the content available to the relevant visitors.

Any content item, when clicked by a user with edit rights for the item, will show a set of tabs at the top for setting basic properties:



.. code:: robotframework
   :class: hidden

   *** Test Cases ***

   Show basic properties tab
       Go to  ${PLONE_URL}

       Wait until element is visible
       ...  css=span.icon-plone-contentmenu-factories
       Click element  css=span.icon-plone-contentmenu-factories

       Wait until element is visible
       ...  css=#plone-contentmenu-factories li.plone-toolbar-submenu-header

       Page should contain element  document
       Click link  document
       Update element style  portal-footer  display  none

       Wait until element is visible
       ...  css=#form-widgets-IDublinCore-title

       Capture and crop page screenshot
       ...  ${CURDIR}/_robot/basicpropertiestabs.png
       ...  css=nav.autotoc-nav

.. figure:: /_robot/basicpropertiestabs.png
   :align: center
   :alt: basicpropertiestabs.png

These basic properties tabs are:

-  *Default* - shows the main data entry panel for the content item
-  *Settings* - shows a small panel for setting whether or not the item will appear in navigation menus and if comments are allowed on the item
-  *Categorization* - shows a panel for creating and setting tags (keywords) for the item
-  *Dates* - shows the publishing date and expiration date for the item
-  *Ownership* - shows a panel for setting creators, contributors, and any copyright information for the item


The input fields under these tabs cover basic descriptive information called **metadata**.
Metadata is sometimes called "data about data."
Plone can use this metadata in a multitude of ways.

Here is the *Categorization* panel, shown for a page content item (would be the same for other content types):

.. code:: robotframework
   :class: hidden

   *** Test Cases ***

   Show edit page categorization
       Click link  Categorization

       Capture and crop page screenshot
       ...  ${CURDIR}/_robot/editpagecategorization.png
       ...  css=#content-core

.. figure:: /_robot/editpagecategorization.png
   :align: center
   :alt: Edit page categorization

The main input field for the panel is for specifying *Tags*, sometimes also known as *Categories*

Create them, just by typing in words or phrases.
Plone will automatically search for existing tags while you type, so you can select already existing tags.
If you want to create a new tag, just hit "enter" after your word (or phrase).

The *Related Items* field lets you set links between content items, which will show as links at the bottom, when a content item is viewed.
This is useful when you don't want to use explicit tags to connect content.

The *Location* field is a geographic location, suitable for use with mapping systems, but appropriate to enter, for general record keeping. Note that this field may not always be present, this is a setting that your site administrator has to enable.

The *Language* choice normally would default to the site setting, but on multilingual web sites, different languages could be used in a mix of content.

The *Dates* panel has fields for the publishing date and the expiration date, effectively start and stop dates for the content if you wish to set them:

.. code:: robotframework
   :class: hidden

   *** Test Cases ***

   Show datessettings
       Click link  Dates

       Capture and crop page screenshot
       ...  ${CURDIR}/_robot/datessettings.png
       ...  css=#content-core

.. figure:: /_robot/datessettings.png
   :align: center
   :alt: Dates Settings


The publication and expiration dates work like this:

-  When an item is past its expiration date, it's marked "expired" in
   red in its document byline when viewed.
-  An item whose publication date is before the current date doesn't get
   extra text in its byline.
-  In both cases, the item is "unpublished", which is not to be confused
   with a workflow state.
-  It merely means the item doesn't show up in listings and searches.
-  These listings include folder listings.
-  However, the owner of the item will keep seeing it, which is handy
   because you like to know what you have lying around in your site.
-  The permission that controls this is Access inactive portal content.
-  Expired items in a folder are marked as such when viewing the
   folder\_contents.
-  There's no quick way of seeing if items in a folder listing are not
   yet published.
-  When you set an unpublished item as the default view for a folder,
   that item will be shown.
-  Unpublishing an item doesn't have any effect for admins. They will
   always see unpublished items in their listings and searches.
-  Giving another regular users rights ("can add", can edit", "can
   review") on the item doesn't make it any less unpublished for those
   users.
-  A practical way for a non-admin user to access an unpublished item is
   directly through its URL.

The *Ownership* panel has three free-form fields for listing creators,
contributors, and information about copyright or ownership rights to the
content:

.. code:: robotframework
   :class: hidden

   *** Test Cases ***

   Show ownershippanel
       Click link  Ownership

       Capture and crop page screenshot
       ...  ${CURDIR}/_robot/ownershippanel.png
       ...  css=#content-core

.. figure:: /_robot/ownershippanel.png
   :align: center
   :alt: Ownership Panel

The *Settings* panel has fields that may vary a bit from content type to
content type, but generally there are input fields controlling whether
or not the item appears in navigation, or if there are comments allowed,
and other similar controls:



.. code:: robotframework
   :class: hidden

   *** Test Cases ***

   Show settingspanel
       Click link  Settings

       Capture and crop page screenshot
       ...  ${CURDIR}/_robot/settingspanel.png
       ...  css=#content-core

.. figure:: /_robot/settingspanel.png
   :align: center
   :alt: Settings panel

You can allow users to edit the "Short name" of content items.

.. note::

    The "Short Name" is part of the URL of a content item.
    That means that no special characters or spaces are allowed in it.
    For experienced web editors, it can be handy to manipulate the Short Name directly in order to generate more memorable or shorter URL's.


Recommendations
---------------

There is no requirement to enter the information specified through these panels, but it is a good idea to do so.
For the *Ownership* panel, providing the data is important for situations where there are several
people involved in content creation, especially if there are multiple creators and contributors working in groups.
You don't always need fields such as publishing and expiration dates, language, and copyrights, but these data should be specified when appropriate.
A content management system can only be as good as the data completeness allows.

Specifying tags requires attention, but if you are able to get in the habit, and are committed to creating a meaningful set of tags, there is a big return on the investment.
The return happens through the use of searching and other facilities in Plone that work off the categorization.
The same holds for setting related items. You'll be able to put your finger on what you need, and you may be able to discover and use relationships within the content.

Exposing Metadata Properties as meta tags in the HTML source
------------------------------------------------------------

From Plone 4 on, in *Site Setup*, there is a check box that will expose the :term:`Dublin Core` metadata properties.
Checking this box will expose the title, description, etc. metadata as meta tags within the
HTML ``<head>``.
For example:

::

    <meta content="short description" name="DC.description" />
    <meta content="short description" name="description" />
    <meta content="text/html" name="DC.format" />
    <meta content="Page" name="DC.type" />
    <meta content="admin" name="DC.creator" />
    <meta content="2009-11-27 17:04:03" name="DC.date.modified" />
    <meta content="2009-11-27 17:04:02" name="DC.date.created" />
    <meta content="en" name="DC.language" />a


The generator will check and obey the so-called *allowAnonymousViewAbout* setting in the :term:`Control Panel` and affects the properties*Creator*, *Contributors* and *Publisher*.

You can read more about `Dublin Core <http://dublincore.org/>`_ and
`HTML
Metatags <http://www.w3.org/TR/html401/struct/global.html#h-7.4.4.2>`_.


