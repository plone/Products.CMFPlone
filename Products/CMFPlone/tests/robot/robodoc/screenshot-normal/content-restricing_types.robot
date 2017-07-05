=============================
Restricting Types in a Folder
=============================

.. include:: _robot.rst

The Add new... menu has a choice for restricting the content types that can be added to the folder.

Restricting types available for adding to a folder is the simplest way to control content creation on a Plone web site.
You may want to restrict content types if your site is going to be worked on by several people.
In this way you can enforce good practices such as putting images in the images folder, or having your "News" items all in the same folder.

.. note::

   Setting restrictions in the very top level, also known as the *root* of the website, is restricted to site administrators.
   That is because this will influence the navigation, and may lead to unwanted side effects.

First, select the last choice in the *Add new...* menu called *Restrictions...*:

.. code:: robotframework
   :class: hidden

   *** Test Cases ***

   Show restrictions
       Go to  ${PLONE_URL}/news

       Click link  css=#plone-contentmenu-factories a

       Wait until element is visible
       ...  css=#plone-contentmenu-factories li.plone-toolbar-submenu-header

       Mouse over  plone-contentmenu-settings
       Update element style  portal-footer  display  none

       Capture and crop page screenshot
       ...  ${CURDIR}/_robot/show-restrictions.png
       ...  css=div.plone-toolbar-container
       ...  css=#plone-contentmenu-factories ul

.. figure:: /_robot/show-restrictions.png
   :align: center
   :alt: show restrictions.png

There are three choices shown for restricting types in the folder:

- Use parent folder settings
- Use portal default
- Select manually

The default choice, to use the setting of the parent folder.
That means when you create a folder and restrict the types that can be added, any subfolders created in the folder will automatically carry these restrictions.

The second choice is a way to reset to the default, unrestricted setting.

The last choice allows selection from a list of available types:

.. code:: robotframework
   :class: hidden

   *** Test Cases ***

   Menu restrictions
       Go to  ${PLONE_URL}/news/folder_constraintypes_form

       Click element  form-widgets-constrain_types_mode


       Capture and crop page screenshot
       ...  ${CURDIR}/_robot/menu-restrictions.png
       ...  css=#main-container


.. figure:: /_robot/menu-restrictions.png
   :align: center
   :alt: menu for setting restrictions.png


Types listed under the *Allowed types* heading are those available on the web site.
The default, as shown, is to allow all types.
Allowed types may be toggled on and off for the folder.

Use of *Secondary types* allows a kind of more detailed control.
For example, if it is preferred to store images in one folder, instead of scattering them in different folders on the web site -- a scheme that some people prefer -- an "Images" folder could be created with the allowed type set to the Image content type *only*.

Likewise an "Company Events" folder could be created to hold only the Event content type.

If left this way, content creators would be forced (or a single web site owner) to follow this strict scheme.

Perhaps some flexibility is desired for images, though. By checking the Image content type under the *Secondary types* heading for the "Company Events" folder, images could be added if really needed, by using the *More...* submenu, which would appear when this mechanism is in place.

The *Secondary types* will be allowed, but be a little more hidden when adding content.
That way, you still have flexibility without confusing part-time editors with too many options.

Some people prefer a heterogeneous mix of content across the web site, with no restrictions.
Others prefer a more regimented approach, restricting types in one organizational scheme or another.
Plone has the flexibility to accommodate a range of designs.

