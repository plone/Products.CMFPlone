Deleting Items
===================

.. include:: _robot.rst

Items may be deleted from a folder with ease.

Sometimes it is necessary to delete a content item. Again, the easiest way to do this is by using "Contents" on the Toolbar.

.. code:: robotframework
   :class: hidden

   *** Test Cases ***

   Edit folder
       Go to  ${PLONE_URL}
       Click element  css=#contentview-folderContents a
       Capture and crop page screenshot
       ...  ${CURDIR}/_robot/foldercontents-delete.png
       ...  css=#content

.. figure:: /_robot/foldercontents-delete.png
   :align: center
   :alt: deleting content

Simply select the content item(s) you want to delete, and press the "Delete" button.

Entire folders may be deleted, so care must be taken with the delete operation!

Plone will warn you if there are other content items in your site that link to the one you are deleting, and will offer to open those in a separate window so you can edit them.

.. note::

    Plone's database will keep a record of deleted items, and in many cases your site administrator will be able to undo an accidental delete.
    However, this will only work if there haven't been many site edits after the delete operation, so if you accidentally delete content, it is important to act soon. Careful site administrators will also have regular backups of the entire site, but getting your content back from there will involve more work. An alternative to deleting content is to 'un-publish' it, so it isn't available to outside visitors anymore.