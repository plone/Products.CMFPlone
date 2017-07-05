Cutting, Copying and Pasting Items
=======================================

.. include:: _robot.rst

Cut, copy, and paste operations involve moving one or more items from one folder to another.

Cut/Paste
---------

Moving items from one area to another on a website is a common task.

It may be that you, or someone else, has created the item in the wrong place.
Or, as time goes by, you decide that reordering content will make your site easier to use, for instance in an intranet when projects and their associated files get transferred to another department in the organisation.

Whatever the reason, Plone makes it easy to transfer individual content items, or even whole folders containing hundreds of items, to another location. All internal links will still work. Plone will even redirect external links (where other websites have linked to this content item directly) in most cases. This mechanism can break, however, if you create a new item with the same title and same location as the one you moved.

The easiest way to move content is by using "Contents" on the Toolbar.

.. code:: robotframework
   :class: hidden

   *** Test Cases ***

   Edit folder
       Go to  ${PLONE_URL}
       Click element  css=#contentview-folderContents a
       Capture and crop page screenshot
       ...  ${CURDIR}/_robot/foldercontents-cutpaste.png
       ...  css=#content

.. figure:: /_robot/foldercontents-cutpaste.png
   :align: center
   :alt: cutting and pasting content

You see an overview of all content in the folder, and in this screenshot that is the content in the top-level or *root* of the site.

You can select individual items, and then use the "Cut" button to cut them. A message "Successfully cut items" will be shown, but the content will still be visible!

Now you can navigate to the folder where you want the content to be, and press the "Paste" button. Only then will the actual moving take place.

The *paste* button remains active, because you would be allowed to continue pasting the content you cut into other places if you wanted.
This could happen in several situations, including when you need to copy one page, for example, as a kind of template or basis document, into several folders.

Copy/Paste
----------

A *copy*/*paste* operation is identical to the *cut*/*paste* operation, except that there is no removal of content from the original folder. It works as you would expect it to work: the original content remains.
If you copy and then paste into the same folder, the (now doubled) new copy of the content will get an automated *short name* of something like "copy_of_originalitem", which you will most likely want to correct by using the "Rename" button.


