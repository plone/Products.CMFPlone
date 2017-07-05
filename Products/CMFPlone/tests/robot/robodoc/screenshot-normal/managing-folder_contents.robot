Folder Contents
====================

.. include:: _robot.rst

The Contents item on the Toolbar shows a list of items in a folder.
It is the place for simple item-by-item actions and for bulk actions such as copy,
cut, paste, move, reorder, etc.

The Contents tab for folders is like "File Manager" or "My Computer" system utilities in Windows and Linux desktops and the "Finder" in Mac OS X, with similar functionality.


.. code:: robotframework
   :class: hidden

   *** Test Cases ***

   Edit folder
       Go to  ${PLONE_URL}
       Click element  css=#contentview-folderContents a
       Capture and crop page screenshot
       ...  ${CURDIR}/_robot/foldercontents.png
       ...  css=#content
       Capture and crop page screenshot
       ...  ${CURDIR}/_robot/foldercontents-columns.png
       ...  css=#btn-attribute-columns
       Capture and crop page screenshot
       ...  ${CURDIR}/_robot/foldercontents-selected.png
       ...  css=#btn-selected-items
       Capture and crop page screenshot
       ...  ${CURDIR}/_robot/foldercontents-rearrange.png
       ...  css=#btn-rearrange
       Capture and crop page screenshot
       ...  ${CURDIR}/_robot/foldercontents-rearrange.png
       ...  css=#btn-rearrange
       Capture and crop page screenshot
       ...  ${CURDIR}/_robot/foldercontents-upload.png
       ...  css=#btn-upload
       Capture and crop page screenshot
       ...  ${CURDIR}/_robot/foldercontents-cut.png
       ...  css=#btn-cut
       Capture and crop page screenshot
       ...  ${CURDIR}/_robot/foldercontents-copy.png
       ...  css=#btn-copy
       Capture and crop page screenshot
       ...  ${CURDIR}/_robot/foldercontents-paste.png
       ...  css=#btn-paste
       Capture and crop page screenshot
       ...  ${CURDIR}/_robot/foldercontents-delete.png
       ...  css=#btn-delete
       Capture and crop page screenshot
       ...  ${CURDIR}/_robot/foldercontents-rename.png
       ...  css=#btn-rename
       Capture and crop page screenshot
       ...  ${CURDIR}/_robot/foldercontents-tags.png
       ...  css=#btn-tags
       Capture and crop page screenshot
       ...  ${CURDIR}/_robot/foldercontents-state.png
       ...  css=#btn-workflow
       Capture and crop page screenshot
       ...  ${CURDIR}/_robot/foldercontents-properties.png
       ...  css=#btn-properties
       Capture and crop page screenshot
       ...  ${CURDIR}/_robot/foldercontents-searchbox.png
       ...  css=#filter

.. figure:: /_robot/foldercontents.png
   :align: center
   :alt: folder contents


The general method is to select one or more items, by checking the checkbox in front of their name, and then performing the desired operation.

*Shift-clicking* to select a range of items works.
This could be very handy for a folder with more than a dozen items or so, and would be
indispensable for folders with hundreds of items.

Let's go over the possibilities one by one:

|columns|

The first icon lets you select the columns to show. This can help you find the right content.

|selected|

The second item in the horizontal bar shows how many items you have selected.

|rearrange|
Press **"Rearrange"** to sort all items in the folder, for instance alphabetically on their title, or chronologically by ``creation date``, ``published date`` or ``date last modified``.

.. warning::

    Be careful when using this option, especially in the root of the site. As folders get re-arranged, it will change the order of the navigation tabs in your site.

|upload|

**"Upload"** allows you to upload one or more files (like images or PDF's) from your computer.

|cut| - |copy| - |paste|

**"Cut"**, **"Copy"** and **"Paste"** do what you :doc:`expect them to do <cutting-copying-and-pasting-items>`.


|delete|

The **"Delete"** button has a red color, since this is a potentially :doc:`dangerous operation <deleting-items>`.

|rename|

 **Rename** will open up a form where you can change the Title and the *short name* for an item. The **Title** can be anything you like, but the **short name** is part of the URL. That means you have to abide by certain rules:

- it cannot contain any spaces or special characters like \* or \\. When you create an item, Plone generates a safe *short name* from the Title, but when you change this later you should take care this remains a valid URL.
- it has to be unique in a folder. You can have two items with the same Title (although it would be confusing), but you cannot have two items with the same *short name* within the same folder. It's perfectly fine to have the same *short name* being used in different folders.

|tags|

 **Tags** allows you to set tags on several items in bulk. This can be a real time-saver.

|state|

**State** will allow you to change the workflow state of one or more items, such as *publishing* them. See the :doc:`chapter on collaboration and workflow </working-with-content/collaboration-and-workflow/index>` for in-depth information.

|properties|

With the **Properties** button you can set things like the *Publication Date*, *Expiration Date*, copyright and other metadata on your content items.

|searchbox|

And finally, use the Query searchbox to locate content items, if you know (part of) the title or any other identifier. This is a very quick way to get to content items in folders with hundreds or thousands of items.

.. |columns| image:: /_robot/foldercontents-columns.png
.. |selected| image:: /_robot/foldercontents-selected.png
.. |rearrange| image:: /_robot/foldercontents-rearrange.png
.. |upload| image:: /_robot/foldercontents-upload.png
.. |cut| image:: /_robot/foldercontents-cut.png
.. |copy| image:: /_robot/foldercontents-copy.png
.. |paste| image:: /_robot/foldercontents-paste.png
.. |delete| image:: /_robot/foldercontents-delete.png
.. |rename| image:: /_robot/foldercontents-rename.png
.. |tags| image:: /_robot/foldercontents-tags.png
.. |state| image:: /_robot/foldercontents-state.png
.. |properties| image:: /_robot/foldercontents-properties.png
.. |searchbox| image:: /_robot/foldercontents-searchbox.png